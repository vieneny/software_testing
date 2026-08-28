package com.example.customerservice.web.dto;

import com.example.customerservice.domain.TicketStatus;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;

public record TransitionTicketRequest(
        @NotNull @PositiveOrZero Long expectedVersion,
        @NotNull TicketStatus targetStatus,
        @NotBlank @Size(max = 100) String operatorName,
        @Size(max = 500) String note
) {
}
