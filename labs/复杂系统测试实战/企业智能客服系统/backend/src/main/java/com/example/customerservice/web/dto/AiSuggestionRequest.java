package com.example.customerservice.web.dto;

import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record AiSuggestionRequest(
        @Size(max = 30) String tone,
        @Pattern(regexp = "zh-CN|en-US", message = "language 只支持 zh-CN 或 en-US") String language
) {
    public String effectiveTone() {
        return tone == null || tone.isBlank() ? "professional" : tone;
    }

    public String effectiveLanguage() {
        return language == null || language.isBlank() ? "zh-CN" : language;
    }
}
