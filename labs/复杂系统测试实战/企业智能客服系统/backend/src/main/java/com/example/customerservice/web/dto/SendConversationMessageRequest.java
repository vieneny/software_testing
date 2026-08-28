package com.example.customerservice.web.dto;

import com.example.customerservice.domain.MessageSenderType;
import com.example.customerservice.domain.MessageVisibility;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;

public record SendConversationMessageRequest(
        @NotNull @PositiveOrZero Long expectedVersion,
        @NotNull MessageSenderType senderType,
        @NotNull MessageVisibility visibility,
        @NotBlank @Size(max = 100) String authorName,
        @NotBlank @Size(max = 5000) String content
) {
}
