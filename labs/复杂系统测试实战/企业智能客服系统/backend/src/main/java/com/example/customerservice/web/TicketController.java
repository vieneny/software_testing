package com.example.customerservice.web;

import com.example.customerservice.common.RequestIdFilter;
import com.example.customerservice.common.IdempotencySupport;
import com.example.customerservice.domain.Tenant;
import com.example.customerservice.domain.TicketStatus;
import com.example.customerservice.service.AiSuggestionService;
import com.example.customerservice.service.TenantService;
import com.example.customerservice.service.TicketService;
import com.example.customerservice.web.dto.AiSuggestionRequest;
import com.example.customerservice.web.dto.AiSuggestionResponse;
import com.example.customerservice.web.dto.AssignTicketRequest;
import com.example.customerservice.web.dto.CreateTicketRequest;
import com.example.customerservice.web.dto.TicketDetailResponse;
import com.example.customerservice.web.dto.TicketSummaryResponse;
import com.example.customerservice.web.dto.TransitionTicketRequest;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestAttribute;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/tickets")
public class TicketController {

    private final TenantService tenantService;
    private final TicketService ticketService;
    private final AiSuggestionService aiSuggestionService;

    public TicketController(
            TenantService tenantService,
            TicketService ticketService,
            AiSuggestionService aiSuggestionService
    ) {
        this.tenantService = tenantService;
        this.ticketService = ticketService;
        this.aiSuggestionService = aiSuggestionService;
    }

    @GetMapping
    public Page<TicketSummaryResponse> list(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @RequestParam(required = false) TicketStatus status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        return ticketService.list(tenantService.requireActive(tenantCode), status, page, size);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public TicketDetailResponse create(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @RequestHeader(
                    name = IdempotencySupport.HEADER_NAME,
                    required = false
            ) String idempotencyKey,
            @Valid @RequestBody CreateTicketRequest request
    ) {
        return ticketService.create(
                tenantService.requireActive(tenantCode),
                request,
                idempotencyKey
        );
    }

    @GetMapping("/{ticketId}")
    public TicketDetailResponse detail(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @PathVariable String ticketId
    ) {
        return ticketService.detail(tenantService.requireActive(tenantCode), ticketId);
    }

    @PostMapping("/{ticketId}/transitions")
    public TicketDetailResponse transition(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @PathVariable String ticketId,
            @Valid @RequestBody TransitionTicketRequest request
    ) {
        return ticketService.transition(
                tenantService.requireActive(tenantCode),
                ticketId,
                request
        );
    }

    @PostMapping("/{ticketId}/assignments")
    public TicketDetailResponse assign(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @PathVariable String ticketId,
            @Valid @RequestBody AssignTicketRequest request
    ) {
        return ticketService.assign(
                tenantService.requireActive(tenantCode),
                ticketId,
                request
        );
    }

    @PostMapping("/{ticketId}/ai-suggestions")
    public AiSuggestionResponse suggest(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @RequestAttribute(RequestIdFilter.ATTRIBUTE_NAME) String requestId,
            @PathVariable String ticketId,
            @Valid @RequestBody(required = false) AiSuggestionRequest request
    ) {
        Tenant tenant = tenantService.requireActive(tenantCode);
        AiSuggestionRequest options = request == null
                ? new AiSuggestionRequest(null, null)
                : request;
        return aiSuggestionService.suggest(tenant, ticketId, options, requestId);
    }
}
