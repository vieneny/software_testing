package com.example.customerservice.config;

import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "application.ai")
public record AiClientProperties(
        String baseUrl,
        String suggestionPath,
        Duration connectTimeout,
        Duration readTimeout
) {
    public AiClientProperties {
        baseUrl = baseUrl == null ? "http://localhost:8000" : baseUrl;
        suggestionPath = suggestionPath == null ? "/api/v1/customer-service/suggest" : suggestionPath;
        connectTimeout = connectTimeout == null ? Duration.ofSeconds(2) : connectTimeout;
        readTimeout = readTimeout == null ? Duration.ofSeconds(20) : readTimeout;
    }
}
