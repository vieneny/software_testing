package com.example.customerservice.web.dto;

import com.example.customerservice.domain.Customer;
import com.example.customerservice.domain.Ticket;
import com.example.customerservice.domain.TicketPriority;
import com.example.customerservice.domain.TicketStatus;
import java.time.Instant;
import java.util.List;

public record TicketDetailResponse(
        String id,
        Long customerId,
        String customerName,
        String customerLevel,
        Long conversationId,
        String title,
        String description,
        String category,
        TicketPriority priority,
        TicketStatus status,
        String assignedAgent,
        Instant dueAt,
        Instant createdAt,
        Instant updatedAt,
        long version,
        List<StatusHistoryResponse> statusHistory
) {
    public static TicketDetailResponse from(
            Ticket ticket,
            Customer customer,
            List<StatusHistoryResponse> history
    ) {
        return new TicketDetailResponse(
                ticket.getPublicId(),
                customer.getId(),
                customer.getDisplayName(),
                customer.getCustomerLevel(),
                ticket.getConversationId(),
                ticket.getTitle(),
                ticket.getDescription(),
                ticket.getCategory(),
                ticket.getPriority(),
                ticket.getStatus(),
                ticket.getAssignedAgent(),
                ticket.getDueAt(),
                ticket.getCreatedAt(),
                ticket.getUpdatedAt(),
                ticket.getVersion(),
                history
        );
    }
}
