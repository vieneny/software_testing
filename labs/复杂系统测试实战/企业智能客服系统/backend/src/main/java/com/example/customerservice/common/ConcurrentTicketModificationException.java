package com.example.customerservice.common;

public class ConcurrentTicketModificationException extends RuntimeException {

    public ConcurrentTicketModificationException() {
        super("工单已被其他坐席更新，请刷新后重试");
    }
}
