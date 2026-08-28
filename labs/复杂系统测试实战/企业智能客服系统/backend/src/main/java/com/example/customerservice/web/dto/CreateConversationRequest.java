package com.example.customerservice.web.dto;

import com.example.customerservice.domain.ConversationChannel;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;

public record CreateConversationRequest(
        @NotNull @Positive Long customerId,
        @NotNull ConversationChannel channel,
        @NotBlank @Size(max = 200) String subject,
        @NotBlank @Size(max = 5000) String initialMessage
) {
}
