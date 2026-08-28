package com.example.customerservice.repository;

import com.example.customerservice.domain.AiSuggestionRecord;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AiSuggestionRecordRepository extends JpaRepository<AiSuggestionRecord, Long> {
}
