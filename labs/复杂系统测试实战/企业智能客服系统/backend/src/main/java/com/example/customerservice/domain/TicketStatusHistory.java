package com.example.customerservice.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;

@Entity
@Table(name = "ticket_status_history", indexes = {
        @Index(name = "idx_ticket_history_ticket", columnList = "ticketId")
})
public class TicketStatusHistory extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long ticketId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private TicketStatus fromStatus;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private TicketStatus toStatus;

    @Column(nullable = false, length = 100)
    private String operatorName;

    @Column(length = 500)
    private String note;

    protected TicketStatusHistory() {
    }

    public TicketStatusHistory(
            Long ticketId,
            TicketStatus fromStatus,
            TicketStatus toStatus,
            String operatorName,
            String note
    ) {
        this.ticketId = ticketId;
        this.fromStatus = fromStatus;
        this.toStatus = toStatus;
        this.operatorName = operatorName;
        this.note = note;
    }

    public TicketStatus getFromStatus() {
        return fromStatus;
    }

    public TicketStatus getToStatus() {
        return toStatus;
    }

    public String getOperatorName() {
        return operatorName;
    }

    public String getNote() {
        return note;
    }
}
