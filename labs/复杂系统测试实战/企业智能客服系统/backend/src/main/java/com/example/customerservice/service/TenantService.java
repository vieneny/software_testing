package com.example.customerservice.service;

import com.example.customerservice.common.InvalidRequestException;
import com.example.customerservice.common.ResourceNotFoundException;
import com.example.customerservice.domain.Tenant;
import com.example.customerservice.repository.TenantRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.regex.Pattern;

@Service
public class TenantService {

    private static final Pattern VALID_TENANT_CODE =
            Pattern.compile("[a-z0-9][a-z0-9_-]{0,63}");

    private final TenantRepository tenantRepository;

    public TenantService(TenantRepository tenantRepository) {
        this.tenantRepository = tenantRepository;
    }

    @Transactional(readOnly = true)
    public Tenant requireActive(String tenantCode) {
        String canonicalCode = tenantCode == null ? "" : tenantCode.strip();
        if (!VALID_TENANT_CODE.matcher(canonicalCode).matches()) {
            throw new InvalidRequestException("X-Tenant-Code 格式不合法");
        }
        return tenantRepository.findByCodeAndActiveTrue(canonicalCode)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "租户不存在或已停用：" + canonicalCode
                ));
    }
}
