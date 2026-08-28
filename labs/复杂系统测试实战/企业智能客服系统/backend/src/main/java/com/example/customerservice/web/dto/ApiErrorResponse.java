package com.example.customerservice.web.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import java.util.Map;

public record ApiErrorResponse(
        Instant timestamp,
        int status,
        String code,
        String message,
        @JsonProperty("request_id") String requestId,
        Map<String, String> fieldErrors
) {
}
