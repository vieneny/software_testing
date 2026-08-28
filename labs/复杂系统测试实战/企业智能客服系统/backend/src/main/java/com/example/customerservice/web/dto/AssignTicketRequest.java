package com.example.customerservice.web.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;

public record AssignTicketRequest(
        @NotNull @PositiveOrZero Long expectedVersion,
        @NotBlank @Size(max = 100) String assignedAgent,
        @NotBlank @Size(max = 100) String operatorName,
        @Size(max = 300) String reason
) {
}
