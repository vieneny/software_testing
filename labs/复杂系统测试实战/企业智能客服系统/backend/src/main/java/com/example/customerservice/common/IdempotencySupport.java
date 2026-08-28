package com.example.customerservice.common;

import com.example.customerservice.domain.IdempotencyRecord;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.regex.Pattern;

public final class IdempotencySupport {

    public static final String HEADER_NAME = "Idempotency-Key";
    private static final Pattern VALID_KEY = Pattern.compile("[A-Za-z0-9._:-]{1,128}");

    private IdempotencySupport() {
    }

    public static String normalize(String supplied) {
        if (supplied == null) {
            return null;
        }
        if (!VALID_KEY.matcher(supplied).matches()) {
            throw new InvalidRequestException(
                    "Idempotency-Key 必须为 1 至 128 位字母、数字或 . _ : -"
            );
        }
        return supplied;
    }

    public static String fingerprint(Object... values) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            for (Object value : values) {
                String text = value == null ? "<null>" : value.toString();
                String framed = text.length() + ":" + text + "|";
                digest.update(framed.getBytes(StandardCharsets.UTF_8));
            }
            return HexFormat.of().formatHex(digest.digest());
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("JVM 不支持 SHA-256", exception);
        }
    }

    public static void requireSameRequest(
            IdempotencyRecord existing,
            String requestFingerprint
    ) {
        if (!existing.getRequestFingerprint().equals(requestFingerprint)) {
            throw new IdempotencyConflictException();
        }
    }
}
