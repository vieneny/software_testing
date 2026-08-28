package com.example.customerservice.common;

public class IdempotencyConflictException extends RuntimeException {

    public IdempotencyConflictException() {
        super("同一个 Idempotency-Key 不能用于不同的请求内容");
    }
}
