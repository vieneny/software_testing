package com.example.customerservice.ai;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;

@JsonIgnoreProperties(ignoreUnknown = true)
public record AiMiddlewareResponse(
        String summary,
        @JsonProperty("suggested_reply") @JsonAlias("suggestedReply") String suggestedReply,
        @JsonProperty("suggested_category") @JsonAlias("suggestedCategory") String suggestedCategory,
        @JsonProperty("suggested_priority") @JsonAlias("suggestedPriority") String suggestedPriority,
        Double confidence,
        @JsonProperty("risk_flags") @JsonAlias("riskFlags") List<String> riskFlags,
        @JsonProperty("knowledge_references") @JsonAlias("knowledgeReferences") List<String> knowledgeReferences,
        @JsonProperty("suggested_actions") @JsonAlias("suggestedActions") List<String> suggestedActions,
        @JsonProperty("must_verify") @JsonAlias("mustVerify") List<String> mustVerify,
        Boolean degraded,
        @JsonProperty("degradation_reason") @JsonAlias("degradationReason") String degradationReason,
        @JsonProperty("api_version") @JsonAlias("apiVersion") String apiVersion,
        @JsonProperty("request_id") @JsonAlias("requestId") String requestId,
        String model
) {
    private static final Set<String> ALLOWED_CATEGORIES = Set.of(
            "ACCOUNT",
            "BILLING",
            "TECHNICAL",
            "SECURITY",
            "PRODUCT",
            "OTHER"
    );
    private static final Set<String> ALLOWED_PRIORITIES = Set.of(
            "LOW",
            "MEDIUM",
            "HIGH",
            "URGENT"
    );
    private static final int MAX_SUMMARY_LENGTH = 2_000;
    private static final int MAX_REPLY_LENGTH = 10_000;
    private static final int MAX_LIST_SIZE = 20;
    private static final int MAX_RISK_FLAG_LENGTH = 100;
    private static final int MAX_REFERENCE_LENGTH = 500;
    private static final int MAX_ACTION_LENGTH = 500;
    private static final int MAX_VERIFICATION_LENGTH = 500;
    private static final int MAX_MODEL_LENGTH = 200;
    private static final Pattern VALID_REQUEST_ID =
            Pattern.compile("[A-Za-z0-9._:-]{1,128}");

    public static AiMiddlewareResponse degraded(String reason) {
        return new AiMiddlewareResponse(
                "AI 服务暂时不可用，请坐席人工判断。",
                "您好，您的问题已记录，我们正在安排人工坐席核实，请稍后留意处理进度。",
                null,
                null,
                0.0,
                List.of("AI_UNAVAILABLE"),
                List.of(),
                List.of("转交人工坐席核实工单事实、客户诉求和下一步处理方式"),
                List.of("人工确认客户身份、问题事实和回复内容后再发送"),
                true,
                reason,
                "v1",
                null,
                "local/fallback"
        );
    }

    public static AiMiddlewareResponse invalidContract(String violationCode) {
        return degraded("AI_RESPONSE_CONTRACT_INVALID:" + violationCode);
    }

    public AiMiddlewareResponse validatedOrDegraded(String expectedRequestId) {
        ContractViolation violation = contractViolation(expectedRequestId);
        if (violation != null) {
            return invalidContract(violation.name());
        }
        if (Boolean.TRUE.equals(degraded)) {
            return degraded("AI_MIDDLEWARE_REPORTED_DEGRADED");
        }

        return new AiMiddlewareResponse(
                summary.strip(),
                suggestedReply.strip(),
                suggestedCategory,
                suggestedPriority,
                confidence,
                normalizedList(riskFlags),
                normalizedList(knowledgeReferences),
                normalizedList(suggestedActions),
                normalizedList(mustVerify),
                false,
                null,
                apiVersion,
                requestId,
                model.strip()
        );
    }

    private ContractViolation contractViolation(String expectedRequestId) {
        if (summary == null || summary.isBlank()) {
            return ContractViolation.SUMMARY_REQUIRED;
        }
        if (summary.length() > MAX_SUMMARY_LENGTH) {
            return ContractViolation.SUMMARY_TOO_LONG;
        }
        if (suggestedReply == null || suggestedReply.isBlank()) {
            return ContractViolation.SUGGESTED_REPLY_REQUIRED;
        }
        if (suggestedReply.length() > MAX_REPLY_LENGTH) {
            return ContractViolation.SUGGESTED_REPLY_TOO_LONG;
        }
        if (suggestedCategory == null) {
            return ContractViolation.CATEGORY_REQUIRED;
        }
        if (!ALLOWED_CATEGORIES.contains(suggestedCategory)) {
            return ContractViolation.CATEGORY_INVALID;
        }
        if (suggestedPriority == null) {
            return ContractViolation.PRIORITY_REQUIRED;
        }
        if (!ALLOWED_PRIORITIES.contains(suggestedPriority)) {
            return ContractViolation.PRIORITY_INVALID;
        }
        if (confidence == null) {
            return ContractViolation.CONFIDENCE_REQUIRED;
        }
        if (!Double.isFinite(confidence) || confidence < 0 || confidence > 1) {
            return ContractViolation.CONFIDENCE_OUT_OF_RANGE;
        }
        ContractViolation riskFlagsViolation = validateList(
                riskFlags,
                MAX_RISK_FLAG_LENGTH,
                ContractViolation.RISK_FLAGS_REQUIRED,
                ContractViolation.RISK_FLAGS_TOO_LARGE,
                ContractViolation.RISK_FLAG_INVALID
        );
        if (riskFlagsViolation != null) {
            return riskFlagsViolation;
        }
        ContractViolation referencesViolation = validateList(
                knowledgeReferences,
                MAX_REFERENCE_LENGTH,
                ContractViolation.KNOWLEDGE_REFERENCES_REQUIRED,
                ContractViolation.KNOWLEDGE_REFERENCES_TOO_LARGE,
                ContractViolation.KNOWLEDGE_REFERENCE_INVALID
        );
        if (referencesViolation != null) {
            return referencesViolation;
        }
        ContractViolation actionsViolation = validateList(
                suggestedActions,
                MAX_ACTION_LENGTH,
                ContractViolation.SUGGESTED_ACTIONS_REQUIRED,
                ContractViolation.SUGGESTED_ACTIONS_TOO_LARGE,
                ContractViolation.SUGGESTED_ACTION_INVALID
        );
        if (actionsViolation != null) {
            return actionsViolation;
        }
        ContractViolation verificationViolation = validateList(
                mustVerify,
                MAX_VERIFICATION_LENGTH,
                ContractViolation.MUST_VERIFY_REQUIRED,
                ContractViolation.MUST_VERIFY_TOO_LARGE,
                ContractViolation.MUST_VERIFY_ITEM_INVALID
        );
        if (verificationViolation != null) {
            return verificationViolation;
        }
        if (mustVerify.isEmpty()) {
            return ContractViolation.MUST_VERIFY_EMPTY;
        }
        if (degraded == null) {
            return ContractViolation.DEGRADED_REQUIRED;
        }
        if (apiVersion == null || apiVersion.isBlank()) {
            return ContractViolation.API_VERSION_REQUIRED;
        }
        if (!"v1".equals(apiVersion)) {
            return ContractViolation.API_VERSION_UNSUPPORTED;
        }
        if (requestId == null || requestId.isBlank()) {
            return ContractViolation.REQUEST_ID_REQUIRED;
        }
        if (!VALID_REQUEST_ID.matcher(requestId).matches()) {
            return ContractViolation.REQUEST_ID_INVALID;
        }
        if (expectedRequestId == null
                || !VALID_REQUEST_ID.matcher(expectedRequestId).matches()) {
            return ContractViolation.EXPECTED_REQUEST_ID_INVALID;
        }
        if (!requestId.equals(expectedRequestId)) {
            return ContractViolation.REQUEST_ID_MISMATCH;
        }
        if (model == null || model.isBlank()) {
            return ContractViolation.MODEL_REQUIRED;
        }
        if (model.length() > MAX_MODEL_LENGTH) {
            return ContractViolation.MODEL_TOO_LONG;
        }
        if (model.chars().anyMatch(Character::isISOControl)) {
            return ContractViolation.MODEL_INVALID;
        }
        return null;
    }

    private static ContractViolation validateList(
            List<String> values,
            int maxEntryLength,
            ContractViolation required,
            ContractViolation tooLarge,
            ContractViolation invalidEntry
    ) {
        if (values == null) {
            return required;
        }
        if (values.size() > MAX_LIST_SIZE) {
            return tooLarge;
        }
        boolean invalid = values.stream()
                .anyMatch(value -> value == null || value.isBlank() || value.length() > maxEntryLength);
        return invalid ? invalidEntry : null;
    }

    private static List<String> normalizedList(List<String> values) {
        return values.stream().map(String::strip).toList();
    }

    private enum ContractViolation {
        SUMMARY_REQUIRED,
        SUMMARY_TOO_LONG,
        SUGGESTED_REPLY_REQUIRED,
        SUGGESTED_REPLY_TOO_LONG,
        CATEGORY_REQUIRED,
        CATEGORY_INVALID,
        PRIORITY_REQUIRED,
        PRIORITY_INVALID,
        CONFIDENCE_REQUIRED,
        CONFIDENCE_OUT_OF_RANGE,
        RISK_FLAGS_REQUIRED,
        RISK_FLAGS_TOO_LARGE,
        RISK_FLAG_INVALID,
        KNOWLEDGE_REFERENCES_REQUIRED,
        KNOWLEDGE_REFERENCES_TOO_LARGE,
        KNOWLEDGE_REFERENCE_INVALID,
        SUGGESTED_ACTIONS_REQUIRED,
        SUGGESTED_ACTIONS_TOO_LARGE,
        SUGGESTED_ACTION_INVALID,
        MUST_VERIFY_REQUIRED,
        MUST_VERIFY_TOO_LARGE,
        MUST_VERIFY_ITEM_INVALID,
        MUST_VERIFY_EMPTY,
        DEGRADED_REQUIRED,
        API_VERSION_REQUIRED,
        API_VERSION_UNSUPPORTED,
        REQUEST_ID_REQUIRED,
        REQUEST_ID_INVALID,
        EXPECTED_REQUEST_ID_INVALID,
        REQUEST_ID_MISMATCH,
        MODEL_REQUIRED,
        MODEL_TOO_LONG,
        MODEL_INVALID
    }
}
