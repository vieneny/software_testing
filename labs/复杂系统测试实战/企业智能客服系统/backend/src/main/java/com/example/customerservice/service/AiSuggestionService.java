package com.example.customerservice.service;

import com.example.customerservice.ai.AiMiddlewareRequest;
import com.example.customerservice.ai.AiMiddlewareResponse;
import com.example.customerservice.ai.AiSuggestionClient;
import com.example.customerservice.domain.AiSuggestionRecord;
import com.example.customerservice.domain.Customer;
import com.example.customerservice.domain.KnowledgeArticle;
import com.example.customerservice.domain.Tenant;
import com.example.customerservice.domain.Ticket;
import com.example.customerservice.repository.AiSuggestionRecordRepository;
import com.example.customerservice.repository.KnowledgeArticleRepository;
import com.example.customerservice.web.dto.AiSuggestionRequest;
import com.example.customerservice.web.dto.AiSuggestionResponse;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AiSuggestionService {

    private final TicketService ticketService;
    private final KnowledgeArticleRepository knowledgeRepository;
    private final AiSuggestionRecordRepository suggestionRecordRepository;
    private final AiSuggestionClient aiSuggestionClient;

    public AiSuggestionService(
            TicketService ticketService,
            KnowledgeArticleRepository knowledgeRepository,
            AiSuggestionRecordRepository suggestionRecordRepository,
            AiSuggestionClient aiSuggestionClient
    ) {
        this.ticketService = ticketService;
        this.knowledgeRepository = knowledgeRepository;
        this.suggestionRecordRepository = suggestionRecordRepository;
        this.aiSuggestionClient = aiSuggestionClient;
    }

    @Transactional
    public AiSuggestionResponse suggest(
            Tenant tenant,
            String publicId,
            AiSuggestionRequest options,
            String requestId
    ) {
        Ticket ticket = ticketService.requireTicket(tenant.getId(), publicId);
        Customer customer = ticketService.requireCustomer(tenant.getId(), ticket.getCustomerId());
        List<KnowledgeArticle> articles = knowledgeRepository
                .findTop5ByTenantIdAndPublishedTrueAndCategoryOrderByUpdatedAtDesc(
                        tenant.getId(),
                        ticket.getCategory()
                );

        AiMiddlewareRequest request = new AiMiddlewareRequest(
                tenant.getCode(),
                ticket.getPublicId(),
                ticket.getTitle(),
                ticket.getDescription(),
                ticket.getCategory(),
                ticket.getPriority().name(),
                customer.getCustomerLevel(),
                options.effectiveTone(),
                options.effectiveLanguage(),
                articles.stream()
                        .map(article -> new AiMiddlewareRequest.KnowledgeContext(
                                article.getTitle(),
                                article.getCategory(),
                                article.getContent()
                        ))
                        .toList()
        );

        AiMiddlewareResponse response = aiSuggestionClient.suggest(request, requestId);
        suggestionRecordRepository.save(new AiSuggestionRecord(
                ticket.getId(),
                response.suggestedReply(),
                response.confidence(),
                response.degraded(),
                response.degradationReason()
        ));

        return new AiSuggestionResponse(
                response.summary(),
                response.suggestedReply(),
                response.suggestedCategory(),
                response.suggestedPriority(),
                response.confidence(),
                response.riskFlags(),
                response.knowledgeReferences(),
                response.suggestedActions(),
                response.mustVerify(),
                response.degraded(),
                response.degradationReason()
        );
    }
}
