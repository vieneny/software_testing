package com.example.customerservice.common;

public class ConcurrentResourceModificationException extends RuntimeException {

    public ConcurrentResourceModificationException(String resourceName) {
        super(resourceName + "已被其他操作者更新，请刷新后重试");
    }
}
