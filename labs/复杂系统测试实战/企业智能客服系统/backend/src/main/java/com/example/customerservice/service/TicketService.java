package com.example.customerservice.service;

import com.example.customerservice.common.BusinessRuleException;
import com.example.customerservice.common.ConcurrentTicketModificationException;
import com.example.customerservice.common.IdempotencySupport;
import com.example.customerservice.common.ResourceNotFoundException;
import com.example.customerservice.domain.AgentAssignment;
import com.example.customerservice.domain.Conversation;
import com.example.customerservice.domain.Customer;
import com.example.customerservice.domain.IdempotencyRecord;
import com.example.customerservice.domain.Tenant;
import com.example.customerservice.domain.Ticket;
import com.example.customerservice.domain.TicketPriority;
import com.example.customerservice.domain.TicketStatus;
import com.example.customerservice.domain.TicketStatusHistory;
import com.example.customerservice.repository.AgentAssignmentRepository;
import com.example.customerservice.repository.ConversationRepository;
import com.example.customerservice.repository.CustomerRepository;
import com.example.customerservice.repository.IdempotencyRecordRepository;
import com.example.customerservice.repository.TenantRepository;
import com.example.customerservice.repository.TicketRepository;
import com.example.customerservice.repository.TicketStatusHistoryRepository;
import com.example.customerservice.web.dto.AssignTicketRequest;
import com.example.customerservice.web.dto.CreateTicketRequest;
import com.example.customerservice.web.dto.StatusHistoryResponse;
import com.example.customerservice.web.dto.TicketDetailResponse;
import com.example.customerservice.web.dto.TicketSummaryResponse;
import com.example.customerservice.web.dto.TransitionTicketRequest;
import java.time.Duration;
import java.time.Instant;
import java.util.EnumMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TicketService {

    private static final Map<TicketStatus, Set<TicketStatus>> ALLOWED_TRANSITIONS = transitions();
    private static final String CREATE_OPERATION = "CREATE_TICKET";

    private final TicketRepository ticketRepository;
    private final CustomerRepository customerRepository;
    private final ConversationRepository conversationRepository;
    private final TicketStatusHistoryRepository historyRepository;
    private final AgentAssignmentRepository assignmentRepository;
    private final IdempotencyRecordRepository idempotencyRepository;
    private final TenantRepository tenantRepository;

    public TicketService(
            TicketRepository ticketRepository,
            CustomerRepository customerRepository,
            ConversationRepository conversationRepository,
            TicketStatusHistoryRepository historyRepository,
            AgentAssignmentRepository assignmentRepository,
            IdempotencyRecordRepository idempotencyRepository,
            TenantRepository tenantRepository
    ) {
        this.ticketRepository = ticketRepository;
        this.customerRepository = customerRepository;
        this.conversationRepository = conversationRepository;
        this.historyRepository = historyRepository;
        this.assignmentRepository = assignmentRepository;
        this.idempotencyRepository = idempotencyRepository;
        this.tenantRepository = tenantRepository;
    }

    @Transactional(readOnly = true)
    public Page<TicketSummaryResponse> list(Tenant tenant, TicketStatus status, int page, int size) {
        PageRequest pageable = PageRequest.of(Math.max(page, 0), Math.min(Math.max(size, 1), 100));
        Page<Ticket> tickets = status == null
                ? ticketRepository.findByTenantIdOrderByUpdatedAtDesc(tenant.getId(), pageable)
                : ticketRepository.findByTenantIdAndStatusOrderByUpdatedAtDesc(tenant.getId(), status, pageable);
        return tickets.map(TicketSummaryResponse::from);
    }

    @Transactional
    public TicketDetailResponse create(
            Tenant tenant,
            CreateTicketRequest request,
            String suppliedIdempotencyKey
    ) {
        String idempotencyKey = IdempotencySupport.normalize(suppliedIdempotencyKey);
        String title = request.title().strip();
        String description = request.description().strip();
        String category = request.category().strip();
        String fingerprint = IdempotencySupport.fingerprint(
                request.customerId(),
                request.conversationId(),
                title,
                description,
                category,
                request.priority()
        );

        if (idempotencyKey != null) {
            tenantRepository.findForUpdateById(tenant.getId())
                    .orElseThrow(() -> new ResourceNotFoundException(
                            "租户不存在或已停用"
                    ));
            var replay = idempotencyRepository
                    .findByTenantIdAndOperationAndIdempotencyKey(
                            tenant.getId(),
                            CREATE_OPERATION,
                            idempotencyKey
                    );
            if (replay.isPresent()) {
                IdempotencySupport.requireSameRequest(replay.get(), fingerprint);
                Ticket existing = requireTicket(
                        tenant.getId(),
                        replay.get().getResourceId()
                );
                return toDetail(
                        existing,
                        requireCustomer(tenant.getId(), existing.getCustomerId())
                );
            }
        }

        Customer customer = requireCustomer(tenant.getId(), request.customerId());
        if (request.conversationId() != null) {
            Conversation conversation = conversationRepository
                    .findByIdAndTenantId(request.conversationId(), tenant.getId())
                    .orElseThrow(() -> new ResourceNotFoundException("会话不存在"));
            if (!conversation.getCustomerId().equals(customer.getId())) {
                throw new BusinessRuleException("会话与客户不匹配");
            }
        }

        Ticket ticket = new Ticket(
                newPublicId(),
                tenant.getId(),
                customer.getId(),
                request.conversationId(),
                title,
                description,
                category,
                request.priority(),
                calculateDueAt(request.priority())
        );
        ticketRepository.save(ticket);
        if (idempotencyKey != null) {
            idempotencyRepository.save(new IdempotencyRecord(
                    tenant.getId(),
                    CREATE_OPERATION,
                    idempotencyKey,
                    fingerprint,
                    ticket.getPublicId()
            ));
        }
        return toDetail(ticket, customer);
    }

    @Transactional(readOnly = true)
    public TicketDetailResponse detail(Tenant tenant, String publicId) {
        Ticket ticket = requireTicket(tenant.getId(), publicId);
        Customer customer = requireCustomer(tenant.getId(), ticket.getCustomerId());
        return toDetail(ticket, customer);
    }

    @Transactional
    public TicketDetailResponse transition(
            Tenant tenant,
            String publicId,
            TransitionTicketRequest request
    ) {
        Ticket ticket = requireTicket(tenant.getId(), publicId);
        requireExpectedVersion(ticket, request.expectedVersion());
        TicketStatus from = ticket.getStatus();
        if (!ALLOWED_TRANSITIONS.getOrDefault(from, Set.of()).contains(request.targetStatus())) {
            throw new BusinessRuleException(
                    "不允许从 " + from + " 流转到 " + request.targetStatus()
            );
        }

        ticket.changeStatus(request.targetStatus());
        historyRepository.save(new TicketStatusHistory(
                ticket.getId(),
                from,
                request.targetStatus(),
                request.operatorName().trim(),
                request.note()
        ));
        ticketRepository.flush();
        return toDetail(ticket, requireCustomer(tenant.getId(), ticket.getCustomerId()));
    }

    @Transactional
    public TicketDetailResponse assign(Tenant tenant, String publicId, AssignTicketRequest request) {
        Ticket ticket = requireTicket(tenant.getId(), publicId);
        requireExpectedVersion(ticket, request.expectedVersion());
        String requestedAgent = request.assignedAgent().trim();
        String previousAgent = ticket.getAssignedAgent();
        if (requestedAgent.equals(previousAgent)) {
            throw new BusinessRuleException("工单已分配给该坐席，无需重复分配");
        }
        ticket.assignTo(requestedAgent);
        assignmentRepository.save(new AgentAssignment(
                ticket.getId(),
                previousAgent,
                requestedAgent,
                request.operatorName().trim(),
                request.reason()
        ));
        ticketRepository.flush();
        return toDetail(ticket, requireCustomer(tenant.getId(), ticket.getCustomerId()));
    }

    @Transactional(readOnly = true)
    public Ticket requireTicket(Long tenantId, String publicId) {
        return ticketRepository.findByPublicIdAndTenantId(publicId, tenantId)
                .orElseThrow(() -> new ResourceNotFoundException("工单不存在：" + publicId));
    }

    @Transactional(readOnly = true)
    public Customer requireCustomer(Long tenantId, Long customerId) {
        return customerRepository.findByIdAndTenantId(customerId, tenantId)
                .orElseThrow(() -> new ResourceNotFoundException("客户不存在：" + customerId));
    }

    private TicketDetailResponse toDetail(Ticket ticket, Customer customer) {
        var history = historyRepository.findByTicketIdOrderByCreatedAtAsc(ticket.getId())
                .stream()
                .map(StatusHistoryResponse::from)
                .toList();
        return TicketDetailResponse.from(ticket, customer, history);
    }

    private String newPublicId() {
        return "TK-" + UUID.randomUUID().toString().replace("-", "").substring(0, 10).toUpperCase();
    }

    private Instant calculateDueAt(TicketPriority priority) {
        long hours = switch (priority) {
            case URGENT -> 2;
            case HIGH -> 8;
            case MEDIUM -> 24;
            case LOW -> 72;
        };
        return Instant.now().plus(Duration.ofHours(hours));
    }

    private void requireExpectedVersion(Ticket ticket, Long expectedVersion) {
        if (expectedVersion == null || ticket.getVersion() != expectedVersion) {
            throw new ConcurrentTicketModificationException();
        }
    }

    private static Map<TicketStatus, Set<TicketStatus>> transitions() {
        EnumMap<TicketStatus, Set<TicketStatus>> result = new EnumMap<>(TicketStatus.class);
        result.put(TicketStatus.NEW, Set.of(TicketStatus.TRIAGED, TicketStatus.IN_PROGRESS));
        result.put(TicketStatus.TRIAGED, Set.of(TicketStatus.IN_PROGRESS, TicketStatus.WAITING_CUSTOMER));
        result.put(TicketStatus.IN_PROGRESS, Set.of(TicketStatus.WAITING_CUSTOMER, TicketStatus.RESOLVED));
        result.put(TicketStatus.WAITING_CUSTOMER, Set.of(TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED));
        result.put(TicketStatus.RESOLVED, Set.of(TicketStatus.CLOSED, TicketStatus.REOPENED));
        result.put(TicketStatus.REOPENED, Set.of(TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED));
        result.put(TicketStatus.CLOSED, Set.of());
        return Map.copyOf(result);
    }
}
