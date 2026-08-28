package com.example.customerservice.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;
import jakarta.persistence.Version;
import java.time.Instant;

@Entity
@Table(name = "tickets", indexes = {
        @Index(name = "idx_ticket_tenant_status", columnList = "tenantId,status"),
        @Index(name = "idx_ticket_tenant_customer", columnList = "tenantId,customerId"),
        @Index(name = "idx_ticket_public_id", columnList = "publicId", unique = true)
})
public class Ticket extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 32)
    private String publicId;

    @Column(nullable = false)
    private Long tenantId;

    @Column(nullable = false)
    private Long customerId;

    private Long conversationId;

    @Column(nullable = false, length = 200)
    private String title;

    @Lob
    @Column(nullable = false)
    private String description;

    @Column(nullable = false, length = 80)
    private String category;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 24)
    private TicketPriority priority;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private TicketStatus status = TicketStatus.NEW;

    @Column(length = 100)
    private String assignedAgent;

    private Instant dueAt;

    @Version
    private long version;

    protected Ticket() {
    }

    public Ticket(
            String publicId,
            Long tenantId,
            Long customerId,
            Long conversationId,
            String title,
            String description,
            String category,
            TicketPriority priority,
            Instant dueAt
    ) {
        this.publicId = publicId;
        this.tenantId = tenantId;
        this.customerId = customerId;
        this.conversationId = conversationId;
        this.title = title;
        this.description = description;
        this.category = category;
        this.priority = priority;
        this.dueAt = dueAt;
    }

    public void changeStatus(TicketStatus status) {
        this.status = status;
    }

    public void assignTo(String agent) {
        this.assignedAgent = agent;
    }

    public Long getId() {
        return id;
    }

    public String getPublicId() {
        return publicId;
    }

    public Long getTenantId() {
        return tenantId;
    }

    public Long getCustomerId() {
        return customerId;
    }

    public Long getConversationId() {
        return conversationId;
    }

    public String getTitle() {
        return title;
    }

    public String getDescription() {
        return description;
    }

    public String getCategory() {
        return category;
    }

    public TicketPriority getPriority() {
        return priority;
    }

    public TicketStatus getStatus() {
        return status;
    }

    public String getAssignedAgent() {
        return assignedAgent;
    }

    public Instant getDueAt() {
        return dueAt;
    }

    public long getVersion() {
        return version;
    }
}
