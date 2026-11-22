// Example extract supplied by CustHub support (2025). Simplified; not production source.
package com.northbridge.custhub.model;

public class CustomerRecord {
    private String customerNumber;      // 10 chars, issued on creation
    private CustomerType customerType;
    private String fullName;
    private LocalDate dateOfBirth;
    private String emailAddress;
    private KycStatus kycStatus;
    private List<Address> addresses;

    public void validate() {
        if (customerNumber == null || customerNumber.length() != 10) {
            throw new ValidationException("customerNumber must be 10 characters");
        }
        if (customerType == CustomerType.INDIVIDUAL && dateOfBirth == null) {
            throw new ValidationException("dateOfBirth is required for individuals");
        }
    }
}

enum CustomerType { INDIVIDUAL, SOLE_TRADER, COMPANY }

enum KycStatus { PENDING, PASSED, FAILED, REFERRED }
