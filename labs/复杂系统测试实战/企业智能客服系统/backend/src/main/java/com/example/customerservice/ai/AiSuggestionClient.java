package com.example.customerservice.ai;

import com.example.customerservice.config.AiClientProperties;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class AiSuggestionClient {

    private final RestClient restClient;
    private final AiClientProperties properties;

    public AiSuggestionClient(RestClient aiRestClient, AiClientProperties properties) {
        this.restClient = aiRestClient;
        this.properties = properties;
    }

    @CircuitBreaker(name = "aiMiddleware", fallbackMethod = "fallback")
    public AiMiddlewareResponse suggest(AiMiddlewareRequest request, String requestId) {
        AiMiddlewareResponse response = restClient.post()
                .uri(properties.suggestionPath())
                .header("X-Request-ID", requestId)
                .body(request)
                .retrieve()
                .body(AiMiddlewareResponse.class);
        if (response == null) {
            return AiMiddlewareResponse.invalidContract("RESPONSE_REQUIRED");
        }
        return response.validatedOrDegraded(requestId);
    }

    AiMiddlewareResponse fallback(
            AiMiddlewareRequest request,
            String requestId,
            Throwable throwable
    ) {
        String exceptionType = throwable == null ? "" : throwable.getClass().getSimpleName();
        if (exceptionType.isBlank()) {
            exceptionType = "UnknownException";
        }
        String reason = "AI_MIDDLEWARE_UNAVAILABLE:" + exceptionType;
        return AiMiddlewareResponse.degraded(reason);
    }
}
