package com.example.customerservice.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record AiMiddlewareRequest(
        @JsonProperty("tenant_code") String tenantCode,
        @JsonProperty("ticket_id") String ticketId,
        String title,
        String description,
        String category,
        String priority,
        @JsonProperty("customer_level") String customerLevel,
        String tone,
        String language,
        @JsonProperty("knowledge_context") List<KnowledgeContext> knowledgeContext
) {
    public record KnowledgeContext(
            String title,
            String category,
            String content
    ) {
    }
}
