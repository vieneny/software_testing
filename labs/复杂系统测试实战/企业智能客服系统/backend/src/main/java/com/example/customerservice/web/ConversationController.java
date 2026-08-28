package com.example.customerservice.web;

import com.example.customerservice.common.IdempotencySupport;
import com.example.customerservice.domain.ConversationState;
import com.example.customerservice.service.ConversationService;
import com.example.customerservice.service.TenantService;
import com.example.customerservice.web.dto.ConversationDetailResponse;
import com.example.customerservice.web.dto.ConversationSummaryResponse;
import com.example.customerservice.web.dto.CreateConversationRequest;
import com.example.customerservice.web.dto.SendConversationMessageRequest;
import com.example.customerservice.web.dto.TransitionConversationRequest;
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
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/conversations")
public class ConversationController {

    private final TenantService tenantService;
    private final ConversationService conversationService;

    public ConversationController(
            TenantService tenantService,
            ConversationService conversationService
    ) {
        this.tenantService = tenantService;
        this.conversationService = conversationService;
    }

    @GetMapping
    public Page<ConversationSummaryResponse> list(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @RequestParam(required = false) ConversationState state,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        return conversationService.list(
                tenantService.requireActive(tenantCode),
                state,
                page,
                size
        );
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ConversationDetailResponse create(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @RequestHeader(
                    name = IdempotencySupport.HEADER_NAME,
                    required = false
            ) String idempotencyKey,
            @Valid @RequestBody CreateConversationRequest request
    ) {
        return conversationService.create(
                tenantService.requireActive(tenantCode),
                request,
                idempotencyKey
        );
    }

    @GetMapping("/{conversationId}")
    public ConversationDetailResponse detail(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @PathVariable Long conversationId,
            @RequestParam(defaultValue = "false") boolean includeInternal
    ) {
        return conversationService.detail(
                tenantService.requireActive(tenantCode),
                conversationId,
                includeInternal
        );
    }

    @PostMapping("/{conversationId}/messages")
    public ConversationDetailResponse addMessage(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @RequestHeader(
                    name = IdempotencySupport.HEADER_NAME,
                    required = false
            ) String idempotencyKey,
            @PathVariable Long conversationId,
            @RequestParam(defaultValue = "false") boolean includeInternal,
            @Valid @RequestBody SendConversationMessageRequest request
    ) {
        return conversationService.addMessage(
                tenantService.requireActive(tenantCode),
                conversationId,
                request,
                idempotencyKey,
                includeInternal
        );
    }

    @PostMapping("/{conversationId}/transitions")
    public ConversationDetailResponse transition(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode,
            @RequestHeader(
                    name = IdempotencySupport.HEADER_NAME,
                    required = false
            ) String idempotencyKey,
            @PathVariable Long conversationId,
            @RequestParam(defaultValue = "false") boolean includeInternal,
            @Valid @RequestBody TransitionConversationRequest request
    ) {
        return conversationService.transition(
                tenantService.requireActive(tenantCode),
                conversationId,
                request,
                idempotencyKey,
                includeInternal
        );
    }
}
