package com.example.customerservice.web.dto;

import com.example.customerservice.domain.Conversation;
import com.example.customerservice.domain.ConversationChannel;
import com.example.customerservice.domain.ConversationMessage;
import com.example.customerservice.domain.ConversationState;
import com.example.customerservice.domain.Customer;
import java.time.Instant;
import java.util.List;

public record ConversationDetailResponse(
        Long id,
        Long customerId,
        String customerName,
        String customerLevel,
        ConversationChannel channel,
        String subject,
        ConversationState state,
        Instant startedAt,
        Instant lastMessageAt,
        Instant createdAt,
        Instant updatedAt,
        long version,
        List<ConversationMessageResponse> messages,
        List<String> linkedTicketIds
) {
    public static ConversationDetailResponse from(
            Conversation conversation,
            Customer customer,
            List<ConversationMessage> messages,
            List<String> linkedTicketIds
    ) {
        return new ConversationDetailResponse(
                conversation.getId(),
                customer.getId(),
                customer.getDisplayName(),
                customer.getCustomerLevel(),
                conversation.getChannel(),
                conversation.getSubject(),
                conversation.getState(),
                conversation.getStartedAt(),
                conversation.getLastMessageAt(),
                conversation.getCreatedAt(),
                conversation.getUpdatedAt(),
                conversation.getVersion(),
                messages.stream().map(ConversationMessageResponse::from).toList(),
                List.copyOf(linkedTicketIds)
        );
    }
}
