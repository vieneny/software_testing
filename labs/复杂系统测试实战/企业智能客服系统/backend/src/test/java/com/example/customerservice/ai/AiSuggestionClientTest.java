package com.example.customerservice.ai;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.customerservice.config.AiClientProperties;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.Test;
import org.springframework.web.client.RestClient;

class AiSuggestionClientTest {

    private static final String VALID_RESPONSE = """
            {
              "summary": "用户遇到登录问题",
              "suggested_reply": "请先重置演示密码。",
              "suggested_category": "ACCOUNT",
              "suggested_priority": "HIGH",
              "confidence": 0.87,
              "risk_flags": [],
              "knowledge_references": ["账号登录故障排查"],
              "suggested_actions": ["核对演示账号状态"],
              "must_verify": ["人工复核后再回复"],
              "degraded": false,
              "degradation_reason": null,
              "api_version": "v1",
              "request_id": "contract-test",
              "model": "mock/customer-service"
            }
            """;

    @Test
    void sendsStableContractToPythonMiddleware() throws Exception {
        try (MockWebServer server = new MockWebServer()) {
            server.enqueue(new MockResponse()
                    .setHeader("Content-Type", "application/json")
                    .setBody("""
                            {
                              "summary": "用户遇到登录问题",
                              "suggested_reply": "请先重置演示密码。",
                              "suggested_category": "ACCOUNT",
                              "suggested_priority": "HIGH",
                              "confidence": 0.87,
                              "risk_flags": [],
                              "knowledge_references": ["账号登录故障排查"],
                              "degraded": false,
                              "degradation_reason": null,
                              "api_version": "v1",
                              "request_id": "request-test-001",
                              "suggested_actions": ["核对演示账号状态"],
                              "must_verify": ["人工复核"],
                              "model": "mock/customer-service"
                            }
                            """));
            server.start();

            AiClientProperties properties = new AiClientProperties(
                    server.url("/").toString(),
                    "/api/v1/customer-service/suggest",
                    Duration.ofSeconds(1),
                    Duration.ofSeconds(2)
            );
            AiSuggestionClient client = new AiSuggestionClient(
                    RestClient.builder().baseUrl(properties.baseUrl()).build(),
                    properties
            );
            AiMiddlewareRequest request = new AiMiddlewareRequest(
                    "demo",
                    "TK-TEST00001",
                    "演示账号无法登录",
                    "纯合成描述",
                    "ACCOUNT",
                    "HIGH",
                    "VIP",
                    "professional",
                    "zh-CN",
                    List.of()
            );

            AiMiddlewareResponse response = client.suggest(request, "request-test-001");
            RecordedRequest recorded = server.takeRequest();

            assertThat(recorded.getPath()).isEqualTo("/api/v1/customer-service/suggest");
            assertThat(recorded.getBody().readUtf8()).contains("\"tenant_code\":\"demo\"");
            assertThat(recorded.getHeader("X-Request-ID")).isEqualTo("request-test-001");
            assertThat(response.suggestedReply()).isEqualTo("请先重置演示密码。");
            assertThat(response.degraded()).isFalse();
            assertThat(response.apiVersion()).isEqualTo("v1");
            assertThat(response.requestId()).isEqualTo("request-test-001");
            assertThat(response.model()).isEqualTo("mock/customer-service");
            assertThat(response.suggestedActions()).containsExactly("核对演示账号状态");
            assertThat(response.mustVerify()).containsExactly("人工复核");
        }
    }

    @Test
    void acceptsTechnicalAndSecurityCategoriesFromProviderContract() throws Exception {
        try (MockWebServer server = new MockWebServer()) {
            server.start();
            AiClientProperties properties = new AiClientProperties(
                    server.url("/").toString(),
                    "/api/v1/customer-service/suggest",
                    Duration.ofSeconds(1),
                    Duration.ofSeconds(2)
            );
            AiSuggestionClient client = new AiSuggestionClient(
                    RestClient.builder().baseUrl(properties.baseUrl()).build(),
                    properties
            );

            for (String category : List.of("TECHNICAL", "SECURITY")) {
                server.enqueue(new MockResponse()
                        .setHeader("Content-Type", "application/json")
                        .setBody(VALID_RESPONSE
                                .replace(
                                        "\"suggested_category\": \"ACCOUNT\"",
                                        "\"suggested_category\": \"" + category + "\""
                                )
                                .replace(
                                        "\"request_id\": \"contract-test\"",
                                        "\"request_id\": \"category-test\""
                                )));

                AiMiddlewareResponse response = client.suggest(sampleRequest(), "category-test");

                assertThat(response.degraded()).isFalse();
                assertThat(response.suggestedCategory()).isEqualTo(category);
            }
        }
    }

    @Test
    void rejectsInvalidSuccessfulResponsesWithoutLeakingUpstreamContent() throws Exception {
        List<InvalidResponse> cases = List.of(
                new InvalidResponse("{}", "SUMMARY_REQUIRED"),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"suggested_reply\": \"请先重置演示密码。\"",
                                "\"suggested_reply\": \"  \""
                        ),
                        "SUGGESTED_REPLY_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"suggested_category\": \"ACCOUNT\"",
                                "\"suggested_category\": null"
                        ),
                        "CATEGORY_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"suggested_category\": \"ACCOUNT\"",
                                "\"suggested_category\": \"INTERNAL_SECRET_CATEGORY\""
                        ),
                        "CATEGORY_INVALID"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"suggested_priority\": \"HIGH\"",
                                "\"suggested_priority\": null"
                        ),
                        "PRIORITY_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"suggested_priority\": \"HIGH\"",
                                "\"suggested_priority\": \"CRITICAL_INTERNAL\""
                        ),
                        "PRIORITY_INVALID"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace("  \"confidence\": 0.87,\n", ""),
                        "CONFIDENCE_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace("\"confidence\": 0.87", "\"confidence\": 1.01"),
                        "CONFIDENCE_OUT_OF_RANGE"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace("  \"risk_flags\": [],\n", ""),
                        "RISK_FLAGS_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace("\"risk_flags\": []", "\"risk_flags\": [null]"),
                        "RISK_FLAG_INVALID"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "  \"knowledge_references\": [\"账号登录故障排查\"],\n",
                                ""
                        ),
                        "KNOWLEDGE_REFERENCES_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"knowledge_references\": [\"账号登录故障排查\"]",
                                "\"knowledge_references\": [\"  \"]"
                        ),
                        "KNOWLEDGE_REFERENCE_INVALID"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "  \"suggested_actions\": [\"核对演示账号状态\"],\n",
                                ""
                        ),
                        "SUGGESTED_ACTIONS_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "[\"核对演示账号状态\"]",
                                repeatedJsonList("动作", 21)
                        ),
                        "SUGGESTED_ACTIONS_TOO_LARGE"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"suggested_actions\": [\"核对演示账号状态\"]",
                                "\"suggested_actions\": [\"  \"]"
                        ),
                        "SUGGESTED_ACTION_INVALID"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "  \"must_verify\": [\"人工复核后再回复\"],\n",
                                ""
                        ),
                        "MUST_VERIFY_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"must_verify\": [\"人工复核后再回复\"]",
                                "\"must_verify\": []"
                        ),
                        "MUST_VERIFY_EMPTY"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "[\"人工复核后再回复\"]",
                                repeatedJsonList("核验", 21)
                        ),
                        "MUST_VERIFY_TOO_LARGE"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"must_verify\": [\"人工复核后再回复\"]",
                                "\"must_verify\": [\"  \"]"
                        ),
                        "MUST_VERIFY_ITEM_INVALID"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"must_verify\": [\"人工复核后再回复\"]",
                                "\"must_verify\": [\"" + "x".repeat(501) + "\"]"
                        ),
                        "MUST_VERIFY_ITEM_INVALID"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace("  \"degraded\": false,\n", ""),
                        "DEGRADED_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace("  \"api_version\": \"v1\",\n", ""),
                        "API_VERSION_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"api_version\": \"v1\"",
                                "\"api_version\": \"v2-secret\""
                        ),
                        "API_VERSION_UNSUPPORTED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace("  \"request_id\": \"contract-test\",\n", ""),
                        "REQUEST_ID_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"request_id\": \"contract-test\"",
                                "\"request_id\": \"unsafe request/id\""
                        ),
                        "REQUEST_ID_INVALID"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"request_id\": \"contract-test\"",
                                "\"request_id\": \"different-secret-id\""
                        ),
                        "REQUEST_ID_MISMATCH"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "  \"request_id\": \"contract-test\",\n"
                                        + "  \"model\": \"mock/customer-service\"\n",
                                "  \"request_id\": \"contract-test\"\n"
                        ),
                        "MODEL_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"model\": \"mock/customer-service\"",
                                "\"model\": \"  \""
                        ),
                        "MODEL_REQUIRED"
                ),
                new InvalidResponse(
                        VALID_RESPONSE.replace(
                                "\"model\": \"mock/customer-service\"",
                                "\"model\": \"" + "x".repeat(201) + "\""
                        ),
                        "MODEL_TOO_LONG"
                )
        );

        try (MockWebServer server = new MockWebServer()) {
            server.start();
            AiClientProperties properties = new AiClientProperties(
                    server.url("/").toString(),
                    "/api/v1/customer-service/suggest",
                    Duration.ofSeconds(1),
                    Duration.ofSeconds(2)
            );
            AiSuggestionClient client = new AiSuggestionClient(
                    RestClient.builder().baseUrl(properties.baseUrl()).build(),
                    properties
            );

            for (InvalidResponse invalid : cases) {
                server.enqueue(new MockResponse()
                        .setHeader("Content-Type", "application/json")
                        .setBody(invalid.body()));

                AiMiddlewareResponse response = client.suggest(sampleRequest(), "contract-test");

                assertThat(response.degraded()).isTrue();
                assertThat(response.degradationReason())
                        .isEqualTo("AI_RESPONSE_CONTRACT_INVALID:" + invalid.violation())
                        .doesNotContain("INTERNAL")
                        .doesNotContain("http");
                assertThat(response.summary()).doesNotContain("用户遇到登录问题");
            }
        }
    }

    @Test
    void fallbackClearlyMarksDegradedResponse() {
        AiClientProperties properties = new AiClientProperties(
                "http://localhost:1",
                "/api/v1/customer-service/suggest",
                Duration.ofMillis(50),
                Duration.ofMillis(50)
        );
        AiSuggestionClient client = new AiSuggestionClient(RestClient.create(), properties);

        AiMiddlewareResponse response = client.fallback(
                new AiMiddlewareRequest(
                        "demo",
                        "TK-TEST00002",
                        "合成问题",
                        "合成描述",
                        "OTHER",
                        "LOW",
                        "NORMAL",
                        "professional",
                        "zh-CN",
                        List.of()
                ),
                "request-test-002",
                new IllegalStateException("mock unavailable")
        );

        assertThat(response.degraded()).isTrue();
        assertThat(response.riskFlags()).contains("AI_UNAVAILABLE");
        assertThat(response.suggestedActions()).isNotEmpty();
        assertThat(response.mustVerify())
                .containsExactly("人工确认客户身份、问题事实和回复内容后再发送");
        assertThat(response.degradationReason())
                .isEqualTo("AI_MIDDLEWARE_UNAVAILABLE:IllegalStateException")
                .doesNotContain("mock unavailable");
    }

    private static AiMiddlewareRequest sampleRequest() {
        return new AiMiddlewareRequest(
                "demo",
                "TK-TEST00003",
                "合成账号无法登录",
                "公开合成描述",
                "ACCOUNT",
                "HIGH",
                "VIP",
                "professional",
                "zh-CN",
                List.of()
        );
    }

    private static String repeatedJsonList(String value, int count) {
        return "[" + String.join(", ", Collections.nCopies(count, "\"" + value + "\"")) + "]";
    }

    private record InvalidResponse(String body, String violation) {
    }
}
