package com.example.customerservice.web.dto;

import com.example.customerservice.domain.ConversationMessage;
import com.example.customerservice.domain.MessageSenderType;
import com.example.customerservice.domain.MessageVisibility;
import java.time.Instant;

public record ConversationMessageResponse(
        Long id,
        long sequence,
        MessageSenderType senderType,
        MessageVisibility visibility,
        String authorName,
        String content,
        Instant createdAt
) {
    public static ConversationMessageResponse from(ConversationMessage message) {
        return new ConversationMessageResponse(
                message.getId(),
                message.getSequenceNumber(),
                message.getSenderType(),
                message.getVisibility(),
                message.getAuthorName(),
                message.getContent(),
                message.getCreatedAt()
        );
    }
}
