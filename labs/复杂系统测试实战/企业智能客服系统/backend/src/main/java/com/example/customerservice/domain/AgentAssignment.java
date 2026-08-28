package com.example.customerservice.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;

@Entity
@Table(name = "agent_assignments", indexes = {
        @Index(name = "idx_assignment_ticket", columnList = "ticketId")
})
public class AgentAssignment extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long ticketId;

    @Column(length = 100)
    private String previousAgent;

    @Column(nullable = false, length = 100)
    private String assignedAgent;

    @Column(nullable = false, length = 100)
    private String operatorName;

    @Column(length = 300)
    private String reason;

    protected AgentAssignment() {
    }

    public AgentAssignment(
            Long ticketId,
            String previousAgent,
            String assignedAgent,
            String operatorName,
            String reason
    ) {
        this.ticketId = ticketId;
        this.previousAgent = previousAgent;
        this.assignedAgent = assignedAgent;
        this.operatorName = operatorName;
        this.reason = reason;
    }
}
