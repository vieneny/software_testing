package com.example.customerservice.web.dto;

import com.example.customerservice.domain.Ticket;
import com.example.customerservice.domain.TicketPriority;
import com.example.customerservice.domain.TicketStatus;
import java.time.Instant;

public record TicketSummaryResponse(
        String id,
        String title,
        String category,
        TicketPriority priority,
        TicketStatus status,
        String assignedAgent,
        Instant dueAt,
        Instant createdAt,
        Instant updatedAt,
        long version
) {
    public static TicketSummaryResponse from(Ticket ticket) {
        return new TicketSummaryResponse(
                ticket.getPublicId(),
                ticket.getTitle(),
                ticket.getCategory(),
                ticket.getPriority(),
                ticket.getStatus(),
                ticket.getAssignedAgent(),
                ticket.getDueAt(),
                ticket.getCreatedAt(),
                ticket.getUpdatedAt(),
                ticket.getVersion()
        );
    }
}
