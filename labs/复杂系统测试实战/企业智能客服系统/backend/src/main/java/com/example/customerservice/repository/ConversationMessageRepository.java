package com.example.customerservice.repository;

import com.example.customerservice.domain.ConversationMessage;
import com.example.customerservice.domain.MessageVisibility;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ConversationMessageRepository
        extends JpaRepository<ConversationMessage, Long> {

    List<ConversationMessage> findByTenantIdAndConversationIdOrderBySequenceNumberAsc(
            Long tenantId,
            Long conversationId
    );

    List<ConversationMessage>
            findByTenantIdAndConversationIdAndVisibilityOrderBySequenceNumberAsc(
                    Long tenantId,
                    Long conversationId,
                    MessageVisibility visibility
            );

    Optional<ConversationMessage>
            findTopByTenantIdAndConversationIdOrderBySequenceNumberDesc(
                    Long tenantId,
                    Long conversationId
            );

    long countByTenantIdAndConversationId(Long tenantId, Long conversationId);
}
