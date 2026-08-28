package com.example.customerservice.config;

import com.example.customerservice.domain.Conversation;
import com.example.customerservice.domain.ConversationChannel;
import com.example.customerservice.domain.ConversationMessage;
import com.example.customerservice.domain.Customer;
import com.example.customerservice.domain.KnowledgeArticle;
import com.example.customerservice.domain.MessageSenderType;
import com.example.customerservice.domain.MessageVisibility;
import com.example.customerservice.domain.Tenant;
import com.example.customerservice.domain.Ticket;
import com.example.customerservice.domain.TicketPriority;
import com.example.customerservice.repository.ConversationRepository;
import com.example.customerservice.repository.ConversationMessageRepository;
import com.example.customerservice.repository.CustomerRepository;
import com.example.customerservice.repository.KnowledgeArticleRepository;
import com.example.customerservice.repository.TenantRepository;
import com.example.customerservice.repository.TicketRepository;
import java.time.Duration;
import java.time.Instant;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DemoDataConfiguration {

    @Bean
    @ConditionalOnProperty(
            name = "application.demo-data-enabled",
            havingValue = "true",
            matchIfMissing = true
    )
    CommandLineRunner seedSyntheticData(
            TenantRepository tenantRepository,
            CustomerRepository customerRepository,
            ConversationRepository conversationRepository,
            ConversationMessageRepository messageRepository,
            KnowledgeArticleRepository knowledgeRepository,
            TicketRepository ticketRepository
    ) {
        return args -> {
            if (tenantRepository.findByCodeAndActiveTrue("demo").isPresent()) {
                return;
            }

            Tenant tenant = tenantRepository.save(new Tenant("demo", "公开学习演示租户"));
            Customer normal = customerRepository.save(new Customer(
                    tenant.getId(),
                    "林小测",
                    "lin.test@example.invalid",
                    "NORMAL"
            ));
            Customer vip = customerRepository.save(new Customer(
                    tenant.getId(),
                    "周同学",
                    "zhou.student@example.invalid",
                    "VIP"
            ));
            Conversation conversation = new Conversation(
                    tenant.getId(),
                    vip.getId(),
                    ConversationChannel.WEB,
                    "演示账号无法登录"
            );
            conversation.recordMessage(
                    MessageSenderType.CUSTOMER,
                    MessageVisibility.CUSTOMER
            );
            conversationRepository.save(conversation);
            messageRepository.save(new ConversationMessage(
                    tenant.getId(),
                    conversation.getId(),
                    1,
                    MessageSenderType.CUSTOMER,
                    MessageVisibility.CUSTOMER,
                    vip.getDisplayName(),
                    "这是公开合成消息：演示账号多次登录失败，希望转人工协助排查。"
            ));

            knowledgeRepository.save(new KnowledgeArticle(
                    tenant.getId(),
                    "账号登录故障排查",
                    "ACCOUNT",
                    "先核对账号状态，再建议重置演示密码；不得索取真实密码、验证码或敏感身份信息。"
            ));
            knowledgeRepository.save(new KnowledgeArticle(
                    tenant.getId(),
                    "退款处理时效说明",
                    "REFUND",
                    "合成商城的退款申请在审核通过后进入模拟支付渠道，演示时效为 1 至 3 个工作日。"
            ));

            Ticket first = new Ticket(
                    "TK-DEMO00001",
                    tenant.getId(),
                    vip.getId(),
                    conversation.getId(),
                    "多次输入正确演示密码仍无法登录",
                    "这是纯合成学习数据：演示用户清理浏览器缓存后依旧收到登录失败提示。",
                    "ACCOUNT",
                    TicketPriority.HIGH,
                    Instant.now().plus(Duration.ofHours(8))
            );
            first.assignTo("坐席-小安");
            ticketRepository.save(first);

            ticketRepository.save(new Ticket(
                    "TK-DEMO00002",
                    tenant.getId(),
                    normal.getId(),
                    null,
                    "查询模拟订单退款进度",
                    "这是纯合成学习数据：模拟订单已提交退款，希望查询当前处理节点。",
                    "REFUND",
                    TicketPriority.MEDIUM,
                    Instant.now().plus(Duration.ofHours(24))
            ));
        };
    }
}
