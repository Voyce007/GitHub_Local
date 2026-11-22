-- STAND-IN schema for TradeDesk, generated from evidence batch loop-02.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-01 Customer · grade A · approved (provisional) — simulated
CREATE TABLE customer (
    customer_number        CHAR(10) NOT NULL,  -- grade A
    customer_type          VARCHAR(20) NOT NULL CHECK (customer_type IN ('INDIVIDUAL', 'SOLE_TRADER', 'COMPANY', 'PUBLIC_BODY')),  -- grade A; CustomerType grade B
    full_name              VARCHAR(200) NOT NULL,  -- grade A
    reg_number             VARCHAR(20),  -- grade A
    credit_status          VARCHAR(20) NOT NULL CHECK (credit_status IN ('APPROVED', 'PROVISIONAL', 'ON_HOLD', 'STOPPED')),  -- grade A; CreditStatus grade B
    credit_limit           NUMERIC(18,2),  -- grade A
    created_timestamp      TIMESTAMP NOT NULL,  -- grade A
    updated_timestamp      TIMESTAMP NOT NULL,  -- grade A
    PRIMARY KEY (customer_number)
);

-- ENT-02 CustomerAddress · grade A · approved (provisional) — simulated
CREATE TABLE customer_address (
    customer_number        CHAR(10) NOT NULL,  -- grade A
    address_type           VARCHAR(20) NOT NULL CHECK (address_type IN ('BILLING', 'DELIVERY')),  -- grade A; AddressType grade C
    line1                  VARCHAR(100) NOT NULL,  -- grade A
    postcode               VARCHAR(10) NOT NULL,  -- grade A
    line2                  VARCHAR(100),  -- grade A
    country_code           CHAR(2) NOT NULL   -- grade A
);

-- Address: no attributes in evidence yet (grade C); see U-05
