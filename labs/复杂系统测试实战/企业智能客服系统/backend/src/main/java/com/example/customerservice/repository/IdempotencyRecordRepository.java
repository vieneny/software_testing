package com.example.customerservice.repository;

import com.example.customerservice.domain.IdempotencyRecord;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface IdempotencyRecordRepository extends JpaRepository<IdempotencyRecord, Long> {

    Optional<IdempotencyRecord> findByTenantIdAndOperationAndIdempotencyKey(
            Long tenantId,
            String operation,
            String idempotencyKey
    );
}
