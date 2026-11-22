// Example extract from the OrderFlow team (2024). Illustrative only.
package com.example.orderflow.domain;

public enum OrderStatus { DRAFT, SUBMITTED, CONFIRMED, FULFILLED, CANCELLED }

public class OrderRequest {
    private String orderId;
    private String customerNumber;
    private String currency;
    private BigDecimal totalAmount;
    private OrderStatus status;
    private List<OrderLine> lines;

    public void validate() {
        if (lines == null || lines.isEmpty()) {
            throw new ValidationException("an order must have at least one line");
        }
    }
}
