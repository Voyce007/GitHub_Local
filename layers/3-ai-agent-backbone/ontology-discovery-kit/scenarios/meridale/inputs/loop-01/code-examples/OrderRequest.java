// Example extract from the ShopFront team (2024). Illustrative only.
package com.meridale.shopfront.orders;

public enum OrderStatus { BASKET, PLACED, PAID, SHIPPED, DELIVERED, CANCELLED }

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
