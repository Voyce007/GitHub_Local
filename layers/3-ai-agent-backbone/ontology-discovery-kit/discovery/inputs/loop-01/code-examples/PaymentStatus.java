// Example extract from the PayRail team (2024). Illustrative only.
package com.northbridge.payrail.domain;

public enum PaymentStatus { RECEIVED, VALIDATED, PENDING, COMPLETED, FAILED, CANCELLED }

public class PaymentInstruction {
    private String paymentId;
    private String debitAccountNumber;
    private BigDecimal amount;
    private String currency;
    private PaymentStatus status;
}
