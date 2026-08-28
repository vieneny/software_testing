package com.example.customerservice.repository;

import com.example.customerservice.domain.Customer;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CustomerRepository extends JpaRepository<Customer, Long> {

    Optional<Customer> findByIdAndTenantId(Long id, Long tenantId);

    List<Customer> findByTenantIdOrderByDisplayNameAsc(Long tenantId);
}
