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
import jakarta.persistence.UniqueConstraint;

@Entity
@Table(
        name = "conversation_messages",
        indexes = {
                @Index(
                        name = "idx_conversation_message_tenant_conversation",
                        columnList = "tenantId,conversationId"
                )
        },
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_conversation_message_sequence",
                        columnNames = {"conversationId", "sequenceNumber"}
                )
        }
)
public class ConversationMessage extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long tenantId;

    @Column(nullable = false)
    private Long conversationId;

    @Column(nullable = false)
    private long sequenceNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 24)
    private MessageSenderType senderType;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 24)
    private MessageVisibility visibility;

    @Column(nullable = false, length = 100)
    private String authorName;

    @Lob
    @Column(nullable = false)
    private String content;

    protected ConversationMessage() {
    }

    public ConversationMessage(
            Long tenantId,
            Long conversationId,
            long sequenceNumber,
            MessageSenderType senderType,
            MessageVisibility visibility,
            String authorName,
            String content
    ) {
        this.tenantId = tenantId;
        this.conversationId = conversationId;
        this.sequenceNumber = sequenceNumber;
        this.senderType = senderType;
        this.visibility = visibility;
        this.authorName = authorName;
        this.content = content;
    }

    public Long getId() {
        return id;
    }

    public Long getTenantId() {
        return tenantId;
    }

    public Long getConversationId() {
        return conversationId;
    }

    public long getSequenceNumber() {
        return sequenceNumber;
    }

    public MessageSenderType getSenderType() {
        return senderType;
    }

    public MessageVisibility getVisibility() {
        return visibility;
    }

    public String getAuthorName() {
        return authorName;
    }

    public String getContent() {
        return content;
    }
}
