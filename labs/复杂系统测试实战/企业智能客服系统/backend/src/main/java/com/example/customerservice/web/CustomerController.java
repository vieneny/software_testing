package com.example.customerservice.web;

import com.example.customerservice.repository.CustomerRepository;
import com.example.customerservice.service.TenantService;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/customers")
public class CustomerController {

    private final TenantService tenantService;
    private final CustomerRepository customerRepository;

    public CustomerController(
            TenantService tenantService,
            CustomerRepository customerRepository
    ) {
        this.tenantService = tenantService;
        this.customerRepository = customerRepository;
    }

    @GetMapping
    public List<CustomerSummary> list(
            @RequestHeader(name = "X-Tenant-Code", defaultValue = "demo") String tenantCode
    ) {
        var tenant = tenantService.requireActive(tenantCode);
        return customerRepository.findByTenantIdOrderByDisplayNameAsc(tenant.getId())
                .stream()
                .map(customer -> new CustomerSummary(
                        customer.getId(),
                        customer.getDisplayName(),
                        customer.getEmail(),
                        customer.getCustomerLevel()
                ))
                .toList();
    }

    public record CustomerSummary(
            Long id,
            String displayName,
            String email,
            String customerLevel
    ) {
    }
}
