package com.example.customerservice.web.dto;

import com.example.customerservice.domain.TicketStatus;
import com.example.customerservice.domain.TicketStatusHistory;
import java.time.Instant;

public record StatusHistoryResponse(
        TicketStatus fromStatus,
        TicketStatus toStatus,
        String operatorName,
        String note,
        Instant occurredAt
) {
    public static StatusHistoryResponse from(TicketStatusHistory history) {
        return new StatusHistoryResponse(
                history.getFromStatus(),
                history.getToStatus(),
                history.getOperatorName(),
                history.getNote(),
                history.getCreatedAt()
        );
    }
}
