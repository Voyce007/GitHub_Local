// Example extract supplied by TradeDesk support (2025). Simplified; not production source.
package com.meridale.tradedesk.model;

public class CustomerRecord {
    private String customerNumber;      // 10 chars, issued on creation
    private CustomerType customerType;
    private String fullName;
    private String regNumber;
    private CreditStatus creditStatus;
    private BigDecimal creditLimit;
    private List<Address> addresses;

    public void validate() {
        if (customerNumber == null || customerNumber.length() != 10) {
            throw new ValidationException("customerNumber must be 10 characters");
        }
        if (customerType == CustomerType.COMPANY && regNumber == null) {
            throw new ValidationException("regNumber is required for companies");
        }
    }
}

enum CustomerType { INDIVIDUAL, SOLE_TRADER, COMPANY, PUBLIC_BODY }

enum CreditStatus { APPROVED, ON_HOLD, STOPPED, PROVISIONAL }
