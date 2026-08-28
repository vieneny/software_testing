package com.example.customerservice.web.dto;

import java.util.List;

public record AiSuggestionResponse(
        String summary,
        String suggestedReply,
        String suggestedCategory,
        String suggestedPriority,
        double confidence,
        List<String> riskFlags,
        List<String> knowledgeReferences,
        List<String> suggestedActions,
        List<String> mustVerify,
        boolean degraded,
        String degradationReason
) {
}
