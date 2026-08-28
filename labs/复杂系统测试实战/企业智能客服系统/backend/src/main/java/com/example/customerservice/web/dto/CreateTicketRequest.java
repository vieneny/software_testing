package com.example.customerservice.web.dto;

import com.example.customerservice.domain.TicketPriority;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record CreateTicketRequest(
        @NotNull Long customerId,
        Long conversationId,
        @NotBlank @Size(max = 200) String title,
        @NotBlank @Size(max = 5000) String description,
        @NotBlank @Size(max = 80) String category,
        @NotNull TicketPriority priority
) {
}
