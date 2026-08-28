package com.example.customerservice.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;

@Entity
@Table(name = "customers", indexes = {
        @Index(name = "idx_customer_tenant_email", columnList = "tenantId,email")
})
public class Customer extends AuditableEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long tenantId;

    @Column(nullable = false, length = 100)
    private String displayName;

    @Column(nullable = false, length = 160)
    private String email;

    @Column(nullable = false, length = 24)
    private String customerLevel = "NORMAL";

    protected Customer() {
    }

    public Customer(Long tenantId, String displayName, String email, String customerLevel) {
        this.tenantId = tenantId;
        this.displayName = displayName;
        this.email = email;
        this.customerLevel = customerLevel;
    }

    public Long getId() {
        return id;
    }

    public Long getTenantId() {
        return tenantId;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getEmail() {
        return email;
    }

    public String getCustomerLevel() {
        return customerLevel;
    }
}
