package com.example.customerservice.web.dto;

import com.example.customerservice.domain.Conversation;
import com.example.customerservice.domain.ConversationChannel;
import com.example.customerservice.domain.ConversationState;
import java.time.Instant;

public record ConversationSummaryResponse(
        Long id,
        Long customerId,
        ConversationChannel channel,
        String subject,
        ConversationState state,
        Instant startedAt,
        Instant lastMessageAt,
        Instant updatedAt,
        long version
) {
    public static ConversationSummaryResponse from(Conversation conversation) {
        return new ConversationSummaryResponse(
                conversation.getId(),
                conversation.getCustomerId(),
                conversation.getChannel(),
                conversation.getSubject(),
                conversation.getState(),
                conversation.getStartedAt(),
                conversation.getLastMessageAt(),
                conversation.getUpdatedAt(),
                conversation.getVersion()
        );
    }
}
