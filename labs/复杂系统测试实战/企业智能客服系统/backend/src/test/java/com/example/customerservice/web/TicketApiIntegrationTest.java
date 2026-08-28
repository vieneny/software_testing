package com.example.customerservice.web;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.matchesPattern;
import static org.hamcrest.Matchers.startsWith;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.customerservice.common.RequestIdFilter;
import com.example.customerservice.repository.AgentAssignmentRepository;
import com.example.customerservice.repository.TenantRepository;
import com.example.customerservice.repository.TicketRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import okhttp3.mockwebserver.Dispatcher;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class TicketApiIntegrationTest {

    private static final String UUID_PATTERN =
            "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}";
    private static final MockWebServer AI_SERVER = new MockWebServer();

    static {
        try {
            AI_SERVER.start();
        } catch (IOException exception) {
            throw new ExceptionInInitializerError(exception);
        }
    }

    @DynamicPropertySource
    static void aiMiddlewareProperties(DynamicPropertyRegistry registry) {
        registry.add("application.ai.base-url", () -> AI_SERVER.url("/").toString());
    }

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private AgentAssignmentRepository assignmentRepository;

    @Autowired
    private TenantRepository tenantRepository;

    @Autowired
    private TicketRepository ticketRepository;

    @AfterAll
    static void stopAiServer() throws IOException {
        AI_SERVER.shutdown();
    }

    @Test
    void healthAndVersionedSyntheticCustomersAreAvailableWithRequestIds() throws Exception {
        MvcResult health = mockMvc.perform(get("/api/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"))
                .andExpect(header().string(RequestIdFilter.HEADER_NAME, matchesPattern(UUID_PATTERN)))
                .andReturn();
        assertThat(health.getResponse().getHeader(RequestIdFilter.HEADER_NAME))
                .matches(UUID_PATTERN);

        mockMvc.perform(get("/api/v1/customers")
                        .header(RequestIdFilter.HEADER_NAME, "customer-list.test:001"))
                .andExpect(status().isOk())
                .andExpect(header().string(
                        RequestIdFilter.HEADER_NAME,
                        "customer-list.test:001"
                ))
                .andExpect(jsonPath("$", hasSize(2)));
    }

    @Test
    void canCreateReadAndTransitionTicketWithIncrementedVersion() throws Exception {
        JsonNode created = createTicket("创建读取和流转");
        String ticketId = created.get("id").asText();
        long initialVersion = created.get("version").asLong();

        mockMvc.perform(get("/api/v1/tickets/{ticketId}", ticketId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title").value("合成数据：创建读取和流转"));

        mockMvc.perform(post("/api/v1/tickets/{ticketId}/transitions", ticketId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "targetStatus": "TRIAGED",
                                  "operatorName": "测试坐席",
                                  "note": "已完成合成场景分诊"
                                }
                                """.formatted(initialVersion)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("TRIAGED"))
                .andExpect(jsonPath("$.version").value(initialVersion + 1))
                .andExpect(jsonPath("$.statusHistory[0].toStatus").value("TRIAGED"));
    }

    @Test
    void invalidStateTransitionReturnsCorrelatedBusinessError() throws Exception {
        JsonNode created = createTicket("非法状态流转");
        String ticketId = created.get("id").asText();
        long version = created.get("version").asLong();

        mockMvc.perform(post("/api/v1/tickets/{ticketId}/transitions", ticketId)
                        .header(RequestIdFilter.HEADER_NAME, "state-error.test:001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "targetStatus": "CLOSED",
                                  "operatorName": "测试坐席",
                                  "note": "验证未解决工单不能直接关闭"
                                }
                                """.formatted(version)))
                .andExpect(status().isConflict())
                .andExpect(header().string(
                        RequestIdFilter.HEADER_NAME,
                        "state-error.test:001"
                ))
                .andExpect(jsonPath("$.code").value("BUSINESS_RULE_VIOLATION"))
                .andExpect(jsonPath("$.request_id").value("state-error.test:001"));
    }

    @Test
    void staleVersionsAreRejectedForAssignmentAndTransition() throws Exception {
        JsonNode created = createTicket("并发版本控制");
        String ticketId = created.get("id").asText();
        long initialVersion = created.get("version").asLong();

        String assignedJson = mockMvc.perform(
                        post("/api/v1/tickets/{ticketId}/assignments", ticketId)
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("""
                                        {
                                          "expectedVersion": %d,
                                          "assignedAgent": "演示坐席甲",
                                          "operatorName": "测试管理员",
                                          "reason": "验证分配后版本递增"
                                        }
                                        """.formatted(initialVersion))
                )
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.assignedAgent").value("演示坐席甲"))
                .andExpect(jsonPath("$.version").value(initialVersion + 1))
                .andReturn()
                .getResponse()
                .getContentAsString();
        long assignedVersion = objectMapper.readTree(assignedJson).get("version").asLong();

        mockMvc.perform(post("/api/v1/tickets/{ticketId}/transitions", ticketId)
                        .header(RequestIdFilter.HEADER_NAME, "stale-transition.test:001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "targetStatus": "TRIAGED",
                                  "operatorName": "过期客户端",
                                  "note": "使用旧版本必须被拒绝"
                                }
                                """.formatted(initialVersion)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("CONCURRENT_MODIFICATION"))
                .andExpect(jsonPath("$.request_id").value("stale-transition.test:001"));

        String transitionedJson = mockMvc.perform(
                        post("/api/v1/tickets/{ticketId}/transitions", ticketId)
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("""
                                        {
                                          "expectedVersion": %d,
                                          "targetStatus": "TRIAGED",
                                          "operatorName": "最新客户端",
                                          "note": "使用当前版本允许流转"
                                        }
                                        """.formatted(assignedVersion))
                )
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.version").value(assignedVersion + 1))
                .andReturn()
                .getResponse()
                .getContentAsString();
        long transitionedVersion = objectMapper.readTree(transitionedJson).get("version").asLong();

        mockMvc.perform(post("/api/v1/tickets/{ticketId}/assignments", ticketId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "assignedAgent": "演示坐席乙",
                                  "operatorName": "过期管理员",
                                  "reason": "再次使用旧版本必须被拒绝"
                                }
                                """.formatted(assignedVersion)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("CONCURRENT_MODIFICATION"));

        mockMvc.perform(get("/api/v1/tickets/{ticketId}", ticketId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.version").value(transitionedVersion))
                .andExpect(jsonPath("$.assignedAgent").value("演示坐席甲"))
                .andExpect(jsonPath("$.status").value("TRIAGED"));
    }

    @Test
    void expectedVersionIsRequiredForMutatingExistingTickets() throws Exception {
        JsonNode created = createTicket("必填版本");
        String ticketId = created.get("id").asText();

        mockMvc.perform(post("/api/v1/tickets/{ticketId}/transitions", ticketId)
                        .header(RequestIdFilter.HEADER_NAME, "validation.test:001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "targetStatus": "TRIAGED",
                                  "operatorName": "缺少版本的客户端"
                                }
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("VALIDATION_FAILED"))
                .andExpect(jsonPath("$.fieldErrors.expectedVersion").exists())
                .andExpect(jsonPath("$.request_id").value("validation.test:001"));
    }

    @Test
    void repeatedAssignmentToSameAgentDoesNotChangeVersionOrWriteAudit() throws Exception {
        JsonNode created = createTicket("重复分配保护");
        String ticketId = created.get("id").asText();
        long initialVersion = created.get("version").asLong();
        Long tenantId = tenantRepository.findByCodeAndActiveTrue("demo")
                .orElseThrow()
                .getId();
        Long internalTicketId = ticketRepository
                .findByPublicIdAndTenantId(ticketId, tenantId)
                .orElseThrow()
                .getId();
        long auditCountBefore = assignmentRepository.countByTicketId(internalTicketId);

        String assignedJson = mockMvc.perform(
                        post("/api/v1/tickets/{ticketId}/assignments", ticketId)
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("""
                                        {
                                          "expectedVersion": %d,
                                          "assignedAgent": "演示重复坐席",
                                          "operatorName": "测试管理员",
                                          "reason": "首次分配应成功"
                                        }
                                        """.formatted(initialVersion))
                )
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.version").value(initialVersion + 1))
                .andReturn()
                .getResponse()
                .getContentAsString();
        long assignedVersion = objectMapper.readTree(assignedJson).get("version").asLong();
        long auditCountAfterFirst = assignmentRepository.countByTicketId(internalTicketId);

        String repeatedBody = """
                {
                  "expectedVersion": %d,
                  "assignedAgent": "演示重复坐席",
                  "operatorName": "重复请求客户端",
                  "reason": "同坐席重复分配必须拒绝"
                }
                """.formatted(assignedVersion);
        for (int attempt = 1; attempt <= 2; attempt++) {
            String requestId = "duplicate-assignment.test:" + attempt;
            mockMvc.perform(post("/api/v1/tickets/{ticketId}/assignments", ticketId)
                            .header(RequestIdFilter.HEADER_NAME, requestId)
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(repeatedBody))
                    .andExpect(status().isConflict())
                    .andExpect(jsonPath("$.code").value("BUSINESS_RULE_VIOLATION"))
                    .andExpect(jsonPath("$.request_id").value(requestId));
        }

        mockMvc.perform(get("/api/v1/tickets/{ticketId}", ticketId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.version").value(assignedVersion))
                .andExpect(jsonPath("$.assignedAgent").value("演示重复坐席"));
        assertThat(auditCountAfterFirst).isEqualTo(auditCountBefore + 1);
        assertThat(assignmentRepository.countByTicketId(internalTicketId))
                .isEqualTo(auditCountAfterFirst);
    }

    @Test
    void canonicalRequestIdReachesResponseAndPythonMiddleware() throws Exception {
        AI_SERVER.setDispatcher(new Dispatcher() {
            @Override
            public MockResponse dispatch(RecordedRequest request) {
                String downstreamRequestId = request.getHeader(RequestIdFilter.HEADER_NAME);
                return new MockResponse()
                        .setHeader("Content-Type", "application/json")
                        .setBody("""
                                {
                                  "summary": "演示工单需要账号排查",
                                  "suggested_reply": "请按公开演示流程重置密码。",
                                  "suggested_category": "ACCOUNT",
                                  "suggested_priority": "HIGH",
                                  "confidence": 0.91,
                                  "risk_flags": [],
                                  "knowledge_references": ["账号登录故障排查"],
                                  "suggested_actions": ["核对账号状态"],
                                  "must_verify": ["人工复核后再回复"],
                                  "degraded": false,
                                  "degradation_reason": null,
                                  "api_version": "v1",
                                  "request_id": "%s",
                                  "model": "mock/customer-service"
                                }
                                """.formatted(downstreamRequestId));
            }
        });

        MvcResult result = mockMvc.perform(
                        post("/api/v1/tickets/TK-DEMO00001/ai-suggestions")
                                .header(RequestIdFilter.HEADER_NAME, "unsafe request/id")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("""
                                        {
                                          "tone": "professional",
                                          "language": "zh-CN"
                                        }
                                        """)
                )
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.degraded").value(false))
                .andExpect(jsonPath("$.suggestedActions[0]").value("核对账号状态"))
                .andExpect(jsonPath("$.mustVerify[0]").value("人工复核后再回复"))
                .andExpect(header().string(
                        RequestIdFilter.HEADER_NAME,
                        matchesPattern(UUID_PATTERN)
                ))
                .andReturn();

        String canonicalRequestId = result.getResponse().getHeader(RequestIdFilter.HEADER_NAME);
        RecordedRequest aiRequest = AI_SERVER.takeRequest(2, TimeUnit.SECONDS);

        assertThat(canonicalRequestId)
                .matches(UUID_PATTERN)
                .isNotEqualTo("unsafe request/id");
        assertThat(aiRequest).isNotNull();
        assertThat(aiRequest.getHeader(RequestIdFilter.HEADER_NAME))
                .isEqualTo(canonicalRequestId);
    }

    @Test
    void pythonMiddlewareFailureDegradesWhileTicketMainFlowRemainsAvailable()
            throws Exception {
        AI_SERVER.setDispatcher(new Dispatcher() {
            @Override
            public MockResponse dispatch(RecordedRequest request) {
                return new MockResponse()
                        .setResponseCode(503)
                        .setHeader("Content-Type", "application/json")
                        .setBody("{\"detail\":\"synthetic unavailable\"}");
            }
        });

        mockMvc.perform(post("/api/v1/tickets/TK-DEMO00001/ai-suggestions")
                        .header(RequestIdFilter.HEADER_NAME, "ai-degraded.test:001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "tone": "professional",
                                  "language": "zh-CN"
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.degraded").value(true))
                .andExpect(jsonPath("$.confidence").value(0))
                .andExpect(jsonPath("$.riskFlags[0]").value("AI_UNAVAILABLE"))
                .andExpect(jsonPath(
                        "$.degradationReason",
                        startsWith("AI_MIDDLEWARE_UNAVAILABLE:")
                ));

        mockMvc.perform(get("/api/v1/tickets/TK-DEMO00001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("TK-DEMO00001"));
    }

    private JsonNode createTicket(String scenario) throws Exception {
        String customersJson = mockMvc.perform(get("/api/v1/customers"))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
        long customerId = objectMapper.readTree(customersJson).get(0).get("id").asLong();

        String createBody = """
                {
                  "customerId": %d,
                  "title": "合成数据：%s",
                  "description": "用于接口测试的公开合成场景，不包含任何真实客户资料。",
                  "category": "BILLING",
                  "priority": "HIGH"
                }
                """.formatted(customerId, scenario);

        String createdJson = mockMvc.perform(post("/api/v1/tickets")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createBody))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.status").value("NEW"))
                .andReturn()
                .getResponse()
                .getContentAsString();
        return objectMapper.readTree(createdJson);
    }
}
