package com.example.customerservice.repository;

import com.example.customerservice.domain.Conversation;
import com.example.customerservice.domain.ConversationState;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import jakarta.persistence.LockModeType;

public interface ConversationRepository extends JpaRepository<Conversation, Long> {

    Optional<Conversation> findByIdAndTenantId(Long id, Long tenantId);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("""
            select conversation
            from Conversation conversation
            where conversation.id = :id and conversation.tenantId = :tenantId
            """)
    Optional<Conversation> findForUpdateByIdAndTenantId(
            @Param("id") Long id,
            @Param("tenantId") Long tenantId
    );

    Page<Conversation> findByTenantIdOrderByUpdatedAtDesc(Long tenantId, Pageable pageable);

    Page<Conversation> findByTenantIdAndStateOrderByUpdatedAtDesc(
            Long tenantId,
            ConversationState state,
            Pageable pageable
    );
}
