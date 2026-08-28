package com.example.customerservice.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "ai_suggestion_records", indexes = {
        @Index(name = "idx_ai_suggestion_ticket", columnList = "ticketId")
})
public class AiSuggestionRecord extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long ticketId;

    @Lob
    @Column(nullable = false)
    private String suggestedReply;

    @Column(nullable = false)
    private double confidence;

    @Column(nullable = false)
    private boolean degraded;

    @Column(length = 500)
    private String degradationReason;

    protected AiSuggestionRecord() {
    }

    public AiSuggestionRecord(
            Long ticketId,
            String suggestedReply,
            double confidence,
            boolean degraded,
            String degradationReason
    ) {
        this.ticketId = ticketId;
        this.suggestedReply = suggestedReply;
        this.confidence = confidence;
        this.degraded = degraded;
        this.degradationReason = degradationReason;
    }
}
