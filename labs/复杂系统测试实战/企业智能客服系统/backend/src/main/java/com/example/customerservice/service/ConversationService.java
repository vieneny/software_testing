package com.example.customerservice.service;

import com.example.customerservice.common.BusinessRuleException;
import com.example.customerservice.common.ConcurrentResourceModificationException;
import com.example.customerservice.common.IdempotencySupport;
import com.example.customerservice.common.ResourceNotFoundException;
import com.example.customerservice.domain.Conversation;
import com.example.customerservice.domain.ConversationMessage;
import com.example.customerservice.domain.ConversationState;
import com.example.customerservice.domain.Customer;
import com.example.customerservice.domain.IdempotencyRecord;
import com.example.customerservice.domain.MessageSenderType;
import com.example.customerservice.domain.MessageVisibility;
import com.example.customerservice.domain.Tenant;
import com.example.customerservice.repository.ConversationMessageRepository;
import com.example.customerservice.repository.ConversationRepository;
import com.example.customerservice.repository.CustomerRepository;
import com.example.customerservice.repository.IdempotencyRecordRepository;
import com.example.customerservice.repository.TenantRepository;
import com.example.customerservice.repository.TicketRepository;
import com.example.customerservice.web.dto.ConversationDetailResponse;
import com.example.customerservice.web.dto.ConversationSummaryResponse;
import com.example.customerservice.web.dto.CreateConversationRequest;
import com.example.customerservice.web.dto.SendConversationMessageRequest;
import com.example.customerservice.web.dto.TransitionConversationRequest;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ConversationService {

    private static final String CREATE_OPERATION = "CREATE_CONVERSATION";

    private final ConversationRepository conversationRepository;
    private final ConversationMessageRepository messageRepository;
    private final CustomerRepository customerRepository;
    private final TicketRepository ticketRepository;
    private final IdempotencyRecordRepository idempotencyRepository;
    private final TenantRepository tenantRepository;

    public ConversationService(
            ConversationRepository conversationRepository,
            ConversationMessageRepository messageRepository,
            CustomerRepository customerRepository,
            TicketRepository ticketRepository,
            IdempotencyRecordRepository idempotencyRepository,
            TenantRepository tenantRepository
    ) {
        this.conversationRepository = conversationRepository;
        this.messageRepository = messageRepository;
        this.customerRepository = customerRepository;
        this.ticketRepository = ticketRepository;
        this.idempotencyRepository = idempotencyRepository;
        this.tenantRepository = tenantRepository;
    }

    @Transactional(readOnly = true)
    public Page<ConversationSummaryResponse> list(
            Tenant tenant,
            ConversationState state,
            int page,
            int size
    ) {
        PageRequest pageable = PageRequest.of(
                Math.max(page, 0),
                Math.min(Math.max(size, 1), 100)
        );
        Page<Conversation> conversations = state == null
                ? conversationRepository.findByTenantIdOrderByUpdatedAtDesc(
                        tenant.getId(),
                        pageable
                )
                : conversationRepository.findByTenantIdAndStateOrderByUpdatedAtDesc(
                        tenant.getId(),
                        state,
                        pageable
                );
        return conversations.map(ConversationSummaryResponse::from);
    }

    @Transactional
    public ConversationDetailResponse create(
            Tenant tenant,
            CreateConversationRequest request,
            String suppliedIdempotencyKey
    ) {
        String idempotencyKey = IdempotencySupport.normalize(suppliedIdempotencyKey);
        String subject = request.subject().strip();
        String initialMessage = request.initialMessage().strip();
        String fingerprint = IdempotencySupport.fingerprint(
                request.customerId(),
                request.channel(),
                subject,
                initialMessage
        );

        if (idempotencyKey != null) {
            lockTenant(tenant.getId());
            var replay = idempotencyRepository
                    .findByTenantIdAndOperationAndIdempotencyKey(
                            tenant.getId(),
                            CREATE_OPERATION,
                            idempotencyKey
                    );
            if (replay.isPresent()) {
                IdempotencySupport.requireSameRequest(replay.get(), fingerprint);
                Long conversationId = parseResourceId(replay.get());
                return toDetail(
                        requireConversation(tenant.getId(), conversationId),
                        false
                );
            }
        }

        Customer customer = requireCustomer(tenant.getId(), request.customerId());
        Conversation conversation = new Conversation(
                tenant.getId(),
                customer.getId(),
                request.channel(),
                subject
        );
        conversation.recordMessage(MessageSenderType.CUSTOMER, MessageVisibility.CUSTOMER);
        conversationRepository.save(conversation);

        ConversationMessage firstMessage = new ConversationMessage(
                tenant.getId(),
                conversation.getId(),
                1,
                MessageSenderType.CUSTOMER,
                MessageVisibility.CUSTOMER,
                customer.getDisplayName(),
                initialMessage
        );
        messageRepository.saveAndFlush(firstMessage);

        if (idempotencyKey != null) {
            idempotencyRepository.save(new IdempotencyRecord(
                    tenant.getId(),
                    CREATE_OPERATION,
                    idempotencyKey,
                    fingerprint,
                    conversation.getId().toString()
            ));
        }
        return toDetail(conversation, false);
    }

    @Transactional(readOnly = true)
    public ConversationDetailResponse detail(
            Tenant tenant,
            Long conversationId,
            boolean includeInternal
    ) {
        return toDetail(
                requireConversation(tenant.getId(), conversationId),
                includeInternal
        );
    }

    @Transactional
    public ConversationDetailResponse addMessage(
            Tenant tenant,
            Long conversationId,
            SendConversationMessageRequest request,
            String suppliedIdempotencyKey,
            boolean includeInternal
    ) {
        Conversation conversation = lockConversation(tenant.getId(), conversationId);
        String idempotencyKey = IdempotencySupport.normalize(suppliedIdempotencyKey);
        String authorName = request.authorName().strip();
        String content = request.content().strip();
        String operation = "CONVERSATION_MESSAGE:" + conversationId;
        String fingerprint = IdempotencySupport.fingerprint(
                request.senderType(),
                request.visibility(),
                authorName,
                content
        );

        if (idempotencyKey != null) {
            var replay = idempotencyRepository
                    .findByTenantIdAndOperationAndIdempotencyKey(
                            tenant.getId(),
                            operation,
                            idempotencyKey
                    );
            if (replay.isPresent()) {
                IdempotencySupport.requireSameRequest(replay.get(), fingerprint);
                return toDetail(conversation, includeInternal);
            }
        }

        requireExpectedVersion(conversation, request.expectedVersion());
        validateNewMessage(conversation, request, authorName, tenant.getId());
        long sequence = nextSequence(tenant.getId(), conversationId);
        ConversationMessage message = new ConversationMessage(
                tenant.getId(),
                conversationId,
                sequence,
                request.senderType(),
                request.visibility(),
                authorName,
                content
        );

        conversation.recordMessage(request.senderType(), request.visibility());
        messageRepository.save(message);
        conversationRepository.flush();
        messageRepository.flush();

        if (idempotencyKey != null) {
            idempotencyRepository.save(new IdempotencyRecord(
                    tenant.getId(),
                    operation,
                    idempotencyKey,
                    fingerprint,
                    message.getId().toString()
            ));
        }
        return toDetail(conversation, includeInternal);
    }

    @Transactional
    public ConversationDetailResponse transition(
            Tenant tenant,
            Long conversationId,
            TransitionConversationRequest request,
            String suppliedIdempotencyKey,
            boolean includeInternal
    ) {
        Conversation conversation = lockConversation(tenant.getId(), conversationId);
        String idempotencyKey = IdempotencySupport.normalize(suppliedIdempotencyKey);
        String operatorName = request.operatorName().strip();
        String note = request.note() == null ? null : request.note().strip();
        String operation = "CONVERSATION_TRANSITION:" + conversationId;
        String fingerprint = IdempotencySupport.fingerprint(
                request.targetState(),
                operatorName,
                note
        );

        if (idempotencyKey != null) {
            var replay = idempotencyRepository
                    .findByTenantIdAndOperationAndIdempotencyKey(
                            tenant.getId(),
                            operation,
                            idempotencyKey
                    );
            if (replay.isPresent()) {
                IdempotencySupport.requireSameRequest(replay.get(), fingerprint);
                return toDetail(conversation, includeInternal);
            }
        }

        requireExpectedVersion(conversation, request.expectedVersion());
        ConversationState from = conversation.getState();
        boolean closing = request.targetState() == ConversationState.CLOSED
                && from != ConversationState.CLOSED;
        boolean reopening = request.targetState() == ConversationState.OPEN
                && from == ConversationState.CLOSED;
        if (!closing && !reopening) {
            throw new BusinessRuleException(
                    "会话只允许从处理中关闭，或从 CLOSED 重新打开"
            );
        }

        long sequence = nextSequence(tenant.getId(), conversationId);
        String transitionContent = from + " -> " + request.targetState();
        if (note != null && !note.isBlank()) {
            transitionContent += "：" + note;
        }
        ConversationMessage auditMessage = new ConversationMessage(
                tenant.getId(),
                conversationId,
                sequence,
                MessageSenderType.SYSTEM,
                MessageVisibility.INTERNAL,
                operatorName,
                transitionContent
        );
        conversation.changeState(request.targetState());
        messageRepository.save(auditMessage);
        conversationRepository.flush();
        messageRepository.flush();

        if (idempotencyKey != null) {
            idempotencyRepository.save(new IdempotencyRecord(
                    tenant.getId(),
                    operation,
                    idempotencyKey,
                    fingerprint,
                    auditMessage.getId().toString()
            ));
        }
        return toDetail(conversation, includeInternal);
    }

    private void validateNewMessage(
            Conversation conversation,
            SendConversationMessageRequest request,
            String authorName,
            Long tenantId
    ) {
        if (conversation.getState() == ConversationState.CLOSED) {
            throw new BusinessRuleException("已关闭会话不能继续发送消息，请先重新打开");
        }
        if (request.senderType() == MessageSenderType.SYSTEM) {
            throw new BusinessRuleException("SYSTEM 消息只能由后端业务流程生成");
        }
        if (request.senderType() == MessageSenderType.CUSTOMER) {
            if (request.visibility() != MessageVisibility.CUSTOMER) {
                throw new BusinessRuleException("客户消息不能标记为内部备注");
            }
            Customer customer = requireCustomer(tenantId, conversation.getCustomerId());
            if (!customer.getDisplayName().equals(authorName)) {
                throw new BusinessRuleException("客户消息的发送者必须与会话客户一致");
            }
        }
    }

    private ConversationDetailResponse toDetail(
            Conversation conversation,
            boolean includeInternal
    ) {
        Customer customer = requireCustomer(
                conversation.getTenantId(),
                conversation.getCustomerId()
        );
        List<ConversationMessage> messages = includeInternal
                ? messageRepository.findByTenantIdAndConversationIdOrderBySequenceNumberAsc(
                        conversation.getTenantId(),
                        conversation.getId()
                )
                : messageRepository
                        .findByTenantIdAndConversationIdAndVisibilityOrderBySequenceNumberAsc(
                                conversation.getTenantId(),
                                conversation.getId(),
                                MessageVisibility.CUSTOMER
                        );
        List<String> linkedTicketIds = ticketRepository
                .findByConversationIdAndTenantIdOrderByCreatedAtAsc(
                        conversation.getId(),
                        conversation.getTenantId()
                )
                .stream()
                .map(ticket -> ticket.getPublicId())
                .toList();
        return ConversationDetailResponse.from(
                conversation,
                customer,
                messages,
                linkedTicketIds
        );
    }

    private Conversation requireConversation(Long tenantId, Long conversationId) {
        return conversationRepository.findByIdAndTenantId(conversationId, tenantId)
                .orElseThrow(() -> new ResourceNotFoundException("会话不存在"));
    }

    private Conversation lockConversation(Long tenantId, Long conversationId) {
        return conversationRepository.findForUpdateByIdAndTenantId(
                        conversationId,
                        tenantId
                )
                .orElseThrow(() -> new ResourceNotFoundException("会话不存在"));
    }

    private Customer requireCustomer(Long tenantId, Long customerId) {
        return customerRepository.findByIdAndTenantId(customerId, tenantId)
                .orElseThrow(() -> new ResourceNotFoundException("客户不存在：" + customerId));
    }

    private long nextSequence(Long tenantId, Long conversationId) {
        return messageRepository
                .findTopByTenantIdAndConversationIdOrderBySequenceNumberDesc(
                        tenantId,
                        conversationId
                )
                .map(message -> message.getSequenceNumber() + 1)
                .orElse(1L);
    }

    private void lockTenant(Long tenantId) {
        tenantRepository.findForUpdateById(tenantId)
                .orElseThrow(() -> new ResourceNotFoundException("租户不存在或已停用"));
    }

    private Long parseResourceId(IdempotencyRecord record) {
        try {
            return Long.valueOf(record.getResourceId());
        } catch (NumberFormatException exception) {
            throw new IllegalStateException("幂等记录关联资源损坏", exception);
        }
    }

    private void requireExpectedVersion(Conversation conversation, Long expectedVersion) {
        if (expectedVersion == null || conversation.getVersion() != expectedVersion) {
            throw new ConcurrentResourceModificationException("会话");
        }
    }
}
