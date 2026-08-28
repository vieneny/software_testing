package com.example.customerservice.web;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.customerservice.domain.Customer;
import com.example.customerservice.domain.Tenant;
import com.example.customerservice.repository.CustomerRepository;
import com.example.customerservice.repository.TenantRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:h2:mem:conversation_api_test;"
                + "MODE=MySQL;DB_CLOSE_DELAY=-1;DATABASE_TO_LOWER=TRUE"
})
@AutoConfigureMockMvc
@ActiveProfiles("test")
class ConversationApiIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private TenantRepository tenantRepository;

    @Autowired
    private CustomerRepository customerRepository;

    @Test
    void createConversationIsIdempotentAndRejectsKeyReuseWithDifferentPayload()
            throws Exception {
        long customerId = firstDemoCustomerId();
        String body = createConversationBody(
                customerId,
                "幂等会话",
                "这是公开合成的首次咨询消息。"
        );

        JsonNode first = postConversation(
                "conversation-create.test:001",
                body,
                "demo"
        );
        JsonNode replay = postConversation(
                "conversation-create.test:001",
                body,
                "demo"
        );

        assertThat(replay.get("id").asLong()).isEqualTo(first.get("id").asLong());
        assertThat(replay.get("version").asLong()).isEqualTo(first.get("version").asLong());
        assertThat(replay.get("messages")).hasSize(1);

        mockMvc.perform(post("/api/v1/conversations")
                        .header("Idempotency-Key", "conversation-create.test:001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createConversationBody(
                                customerId,
                                "另一个会话内容",
                                "同一个幂等键不能创建不同资源。"
                        )))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("IDEMPOTENCY_KEY_REUSED"));

        mockMvc.perform(post("/api/v1/conversations")
                        .header("Idempotency-Key", "invalid key/with spaces")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("INVALID_REQUEST"));
    }

    @Test
    void customerMessageAgentReplyAndInternalNoteFormAnIsolatedTimeline()
            throws Exception {
        JsonNode created = createConversation("公开回复与内部备注");
        long conversationId = created.get("id").asLong();
        long initialVersion = created.get("version").asLong();

        String publicReply = """
                {
                  "expectedVersion": %d,
                  "senderType": "AGENT",
                  "visibility": "CUSTOMER",
                  "authorName": "演示坐席甲",
                  "content": "您好，已收到这条公开合成咨询，正在核对演示数据。"
                }
                """.formatted(initialVersion);
        JsonNode replied = postMessage(
                conversationId,
                "conversation-message.test:public",
                publicReply
        );
        assertThat(replied.get("state").asText()).isEqualTo("WAITING_CUSTOMER");
        assertThat(replied.get("version").asLong()).isEqualTo(initialVersion + 1);
        assertThat(replied.get("messages")).hasSize(2);

        JsonNode replayed = postMessage(
                conversationId,
                "conversation-message.test:public",
                publicReply
        );
        assertThat(replayed.get("version").asLong())
                .isEqualTo(replied.get("version").asLong());
        assertThat(replayed.get("messages")).hasSize(2);

        long repliedVersion = replied.get("version").asLong();
        String internalNote = """
                {
                  "expectedVersion": %d,
                  "senderType": "AGENT",
                  "visibility": "INTERNAL",
                  "authorName": "演示坐席甲",
                  "content": "内部备注：仅记录公开合成的排查步骤，不能展示给客户。"
                }
                """.formatted(repliedVersion);
        JsonNode noted = postMessage(
                conversationId,
                "conversation-message.test:internal",
                internalNote
        );
        assertThat(noted.get("state").asText()).isEqualTo("WAITING_CUSTOMER");
        assertThat(noted.get("version").asLong()).isEqualTo(repliedVersion + 1);
        assertThat(noted.get("messages")).hasSize(3);
        assertThat(noted.get("messages").get(2).get("visibility").asText())
                .isEqualTo("INTERNAL");

        mockMvc.perform(get("/api/v1/conversations/{id}", conversationId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.messages", hasSize(2)))
                .andExpect(jsonPath("$.messages[0].visibility").value("CUSTOMER"))
                .andExpect(jsonPath("$.messages[1].visibility").value("CUSTOMER"));

        mockMvc.perform(get("/api/v1/conversations/{id}", conversationId)
                        .queryParam("includeInternal", "true"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.messages", hasSize(3)))
                .andExpect(jsonPath("$.messages[2].visibility").value("INTERNAL"));

        mockMvc.perform(post(
                                "/api/v1/conversations/{id}/messages",
                                conversationId
                        )
                        .header("Idempotency-Key", "conversation-message.test:internal")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(internalNote.replace("排查步骤", "另一份内容")))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("IDEMPOTENCY_KEY_REUSED"));
    }

    @Test
    void staleVersionSenderRulesAndClosedConversationAreRejected() throws Exception {
        JsonNode created = createConversation("状态与并发保护");
        long conversationId = created.get("id").asLong();
        long version = created.get("version").asLong();

        mockMvc.perform(post(
                                "/api/v1/conversations/{id}/messages",
                                conversationId
                        )
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "senderType": "CUSTOMER",
                                  "visibility": "INTERNAL",
                                  "authorName": "林小测",
                                  "content": "客户不能写内部备注。"
                                }
                                """.formatted(version)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("BUSINESS_RULE_VIOLATION"));

        mockMvc.perform(post(
                                "/api/v1/conversations/{id}/messages",
                                conversationId
                        )
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "senderType": "SYSTEM",
                                  "visibility": "INTERNAL",
                                  "authorName": "伪造系统",
                                  "content": "外部请求不能伪造系统消息。"
                                }
                                """.formatted(version)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("BUSINESS_RULE_VIOLATION"));

        String closedJson = mockMvc.perform(post(
                                "/api/v1/conversations/{id}/transitions",
                                conversationId
                        )
                        .queryParam("includeInternal", "true")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "targetState": "CLOSED",
                                  "operatorName": "演示坐席甲",
                                  "note": "公开合成场景处理完成"
                                }
                                """.formatted(version)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.state").value("CLOSED"))
                .andExpect(jsonPath("$.messages[1].visibility").value("INTERNAL"))
                .andReturn()
                .getResponse()
                .getContentAsString();
        long closedVersion = objectMapper.readTree(closedJson).get("version").asLong();

        mockMvc.perform(post(
                                "/api/v1/conversations/{id}/messages",
                                conversationId
                        )
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "senderType": "AGENT",
                                  "visibility": "CUSTOMER",
                                  "authorName": "演示坐席甲",
                                  "content": "关闭后不能继续回复。"
                                }
                                """.formatted(closedVersion)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("BUSINESS_RULE_VIOLATION"));

        mockMvc.perform(post(
                                "/api/v1/conversations/{id}/transitions",
                                conversationId
                        )
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "targetState": "OPEN",
                                  "operatorName": "过期客户端"
                                }
                                """.formatted(version)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("CONCURRENT_MODIFICATION"));
    }

    @Test
    void customerMessageMutationDoesNotLeakExistingInternalNotes() throws Exception {
        JsonNode created = createConversation("客户消息响应隔离内部备注");
        long conversationId = created.get("id").asLong();
        String internalNote = """
                {
                  "expectedVersion": %d,
                  "senderType": "AGENT",
                  "visibility": "INTERNAL",
                  "authorName": "演示坐席甲",
                  "content": "内部备注：默认消息响应不得向客户返回本条内容。"
                }
                """.formatted(created.get("version").asLong());
        JsonNode noted = postMessage(
                conversationId,
                "conversation-message.test:customer-visibility-note",
                internalNote
        );

        mockMvc.perform(post(
                                "/api/v1/conversations/{id}/messages",
                                conversationId
                        )
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "expectedVersion": %d,
                                  "senderType": "CUSTOMER",
                                  "visibility": "CUSTOMER",
                                  "authorName": "%s",
                                  "content": "这是客户补充的公开合成消息。"
                                }
                                """.formatted(
                                noted.get("version").asLong(),
                                noted.get("customerName").asText()
                        )))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.messages", hasSize(2)))
                .andExpect(jsonPath("$.messages[0].visibility").value("CUSTOMER"))
                .andExpect(jsonPath("$.messages[1].visibility").value("CUSTOMER"));
    }

    @Test
    void conversationCanCreateExactlyOneLinkedTicketOnRetry() throws Exception {
        JsonNode conversation = createConversation("会话升级工单");
        long conversationId = conversation.get("id").asLong();
        long customerId = conversation.get("customerId").asLong();
        String ticketBody = """
                {
                  "customerId": %d,
                  "conversationId": %d,
                  "title": "合成会话升级为客服工单",
                  "description": "由公开合成会话创建，用于验证完整纵向链路。",
                  "category": "ACCOUNT",
                  "priority": "HIGH"
                }
                """.formatted(customerId, conversationId);

        JsonNode first = postTicket("ticket-create.from-conversation:001", ticketBody);
        JsonNode replay = postTicket("ticket-create.from-conversation:001", ticketBody);
        assertThat(replay.get("id").asText()).isEqualTo(first.get("id").asText());

        mockMvc.perform(get("/api/v1/conversations/{id}", conversationId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.linkedTicketIds", hasSize(1)))
                .andExpect(jsonPath("$.linkedTicketIds[0]").value(first.get("id").asText()));

        mockMvc.perform(post("/api/v1/tickets")
                        .header("Idempotency-Key", "ticket-create.from-conversation:001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(ticketBody.replace("HIGH", "URGENT")))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.code").value("IDEMPOTENCY_KEY_REUSED"));
    }

    @Test
    void tenantBoundaryReturnsNotFoundInsteadOfLeakingConversation() throws Exception {
        Tenant isolatedTenant = tenantRepository.save(
                new Tenant("conversation-isolated", "隔离测试租户")
        );
        Customer isolatedCustomer = customerRepository.save(new Customer(
                isolatedTenant.getId(),
                "隔离测试客户",
                "isolated@example.invalid",
                "NORMAL"
        ));
        JsonNode isolatedConversation = postConversation(
                "conversation-isolated.create:001",
                createConversationBody(
                        isolatedCustomer.getId(),
                        "隔离租户会话",
                        "仅属于隔离测试租户的公开合成内容。"
                ),
                "conversation-isolated"
        );
        long isolatedId = isolatedConversation.get("id").asLong();

        mockMvc.perform(get("/api/v1/conversations/{id}", isolatedId))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.code").value("RESOURCE_NOT_FOUND"));

        mockMvc.perform(get("/api/v1/conversations/{id}", isolatedId)
                        .header("X-Tenant-Code", "conversation-isolated"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.customerName").value("隔离测试客户"));

        mockMvc.perform(post("/api/v1/conversations")
                        .header("X-Tenant-Code", "conversation-isolated")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createConversationBody(
                                firstDemoCustomerId(),
                                "跨租户客户引用",
                                "不得引用其他租户的客户。"
                        )))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.code").value("RESOURCE_NOT_FOUND"));
    }

    private JsonNode createConversation(String scenario) throws Exception {
        return postConversation(
                null,
                createConversationBody(
                        firstDemoCustomerId(),
                        scenario,
                        "这是用于测试的公开合成客户咨询，不包含真实资料。"
                ),
                "demo"
        );
    }

    private JsonNode postConversation(String key, String body, String tenantCode)
            throws Exception {
        var request = post("/api/v1/conversations")
                .header("X-Tenant-Code", tenantCode)
                .contentType(MediaType.APPLICATION_JSON)
                .content(body);
        if (key != null) {
            request.header("Idempotency-Key", key);
        }
        String json = mockMvc.perform(request)
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.state").value("WAITING_AGENT"))
                .andExpect(jsonPath("$.messages", hasSize(1)))
                .andReturn()
                .getResponse()
                .getContentAsString();
        return objectMapper.readTree(json);
    }

    private JsonNode postMessage(long conversationId, String key, String body)
            throws Exception {
        String json = mockMvc.perform(post(
                                "/api/v1/conversations/{id}/messages",
                                conversationId
                        )
                        .queryParam("includeInternal", "true")
                        .header("Idempotency-Key", key)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
        return objectMapper.readTree(json);
    }

    private JsonNode postTicket(String key, String body) throws Exception {
        String json = mockMvc.perform(post("/api/v1/tickets")
                        .header("Idempotency-Key", key)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().isCreated())
                .andReturn()
                .getResponse()
                .getContentAsString();
        return objectMapper.readTree(json);
    }

    private long firstDemoCustomerId() throws Exception {
        String json = mockMvc.perform(get("/api/v1/customers"))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
        return objectMapper.readTree(json).get(0).get("id").asLong();
    }

    private String createConversationBody(
            long customerId,
            String subject,
            String initialMessage
    ) {
        return """
                {
                  "customerId": %d,
                  "channel": "WEB",
                  "subject": "%s",
                  "initialMessage": "%s"
                }
                """.formatted(customerId, subject, initialMessage);
    }
}
