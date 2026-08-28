package com.example.customerservice.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;

@Entity
@Table(
        name = "idempotency_records",
        indexes = {
                @Index(
                        name = "idx_idempotency_tenant_operation",
                        columnList = "tenantId,operation"
                )
        },
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_idempotency_tenant_operation_key",
                        columnNames = {"tenantId", "operation", "idempotencyKey"}
                )
        }
)
public class IdempotencyRecord extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long tenantId;

    @Column(nullable = false, length = 100)
    private String operation;

    @Column(nullable = false, length = 128)
    private String idempotencyKey;

    @Column(nullable = false, length = 64)
    private String requestFingerprint;

    @Column(nullable = false, length = 64)
    private String resourceId;

    protected IdempotencyRecord() {
    }

    public IdempotencyRecord(
            Long tenantId,
            String operation,
            String idempotencyKey,
            String requestFingerprint,
            String resourceId
    ) {
        this.tenantId = tenantId;
        this.operation = operation;
        this.idempotencyKey = idempotencyKey;
        this.requestFingerprint = requestFingerprint;
        this.resourceId = resourceId;
    }

    public String getRequestFingerprint() {
        return requestFingerprint;
    }

    public String getResourceId() {
        return resourceId;
    }
}
