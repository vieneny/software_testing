package com.example.customerservice.repository;

import com.example.customerservice.domain.Ticket;
import com.example.customerservice.domain.TicketStatus;
import java.util.Optional;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TicketRepository extends JpaRepository<Ticket, Long> {

    Page<Ticket> findByTenantIdOrderByUpdatedAtDesc(Long tenantId, Pageable pageable);

    Page<Ticket> findByTenantIdAndStatusOrderByUpdatedAtDesc(
            Long tenantId,
            TicketStatus status,
            Pageable pageable
    );

    Optional<Ticket> findByPublicIdAndTenantId(String publicId, Long tenantId);

    List<Ticket> findByConversationIdAndTenantIdOrderByCreatedAtAsc(
            Long conversationId,
            Long tenantId
    );
}
