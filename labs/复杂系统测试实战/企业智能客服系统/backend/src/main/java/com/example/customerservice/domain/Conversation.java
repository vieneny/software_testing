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
import jakarta.persistence.Version;
import java.time.Instant;

@Entity
@Table(name = "conversations", indexes = {
        @Index(name = "idx_conversation_tenant_customer", columnList = "tenantId,customerId")
})
public class Conversation extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long tenantId;

    @Column(nullable = false)
    private Long customerId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 24)
    private ConversationChannel channel;

    @Column(nullable = false, length = 200)
    private String subject;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 24)
    private ConversationState state = ConversationState.OPEN;

    @Column(nullable = false)
    private Instant startedAt = Instant.now();

    @Column(nullable = false)
    private Instant lastMessageAt = Instant.now();

    @Version
    private long version;

    protected Conversation() {
    }

    public Conversation(Long tenantId, Long customerId, ConversationChannel channel, String subject) {
        this.tenantId = tenantId;
        this.customerId = customerId;
        this.channel = channel;
        this.subject = subject;
    }

    public void recordMessage(MessageSenderType senderType, MessageVisibility visibility) {
        if (visibility == MessageVisibility.CUSTOMER) {
            state = senderType == MessageSenderType.CUSTOMER
                    ? ConversationState.WAITING_AGENT
                    : ConversationState.WAITING_CUSTOMER;
        }
        lastMessageAt = Instant.now();
    }

    public void changeState(ConversationState targetState) {
        state = targetState;
        lastMessageAt = Instant.now();
    }

    public Long getId() {
        return id;
    }

    public Long getTenantId() {
        return tenantId;
    }

    public Long getCustomerId() {
        return customerId;
    }

    public ConversationChannel getChannel() {
        return channel;
    }

    public String getSubject() {
        return subject;
    }

    public ConversationState getState() {
        return state;
    }

    public Instant getStartedAt() {
        return startedAt;
    }

    public Instant getLastMessageAt() {
        return lastMessageAt;
    }

    public long getVersion() {
        return version;
    }
}
