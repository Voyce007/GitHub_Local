-- STAND-IN schema for TradeDesk, generated from evidence batch loop-01.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-01 Customer · grade B · approved (provisional) — simulated
CREATE TABLE customer (
    customer_number        CHAR(10) NOT NULL,  -- grade B
    customer_type          VARCHAR(20) NOT NULL CHECK (customer_type IN ('INDIVIDUAL', 'SOLE_TRADER', 'COMPANY', 'PUBLIC_BODY')),  -- grade B; CustomerType grade B
    full_name              VARCHAR(200) NOT NULL,  -- grade B
    reg_number             VARCHAR(20),  -- grade B
    credit_status          VARCHAR(20) NOT NULL,  -- grade B; CreditStatus grade X — values contested
    credit_limit           NUMERIC(18,2),  -- grade B
    created_timestamp      TIMESTAMP NOT NULL,  -- grade C
    PRIMARY KEY (customer_number)
);

-- ENT-02 CustomerAddress · grade C · approved (provisional) — simulated
CREATE TABLE customer_address (
    customer_number        CHAR(10) NOT NULL,  -- grade C
    address_type           VARCHAR(20) NOT NULL CHECK (address_type IN ('BILLING', 'DELIVERY')),  -- grade C; AddressType grade C
    line1                  VARCHAR(100) NOT NULL,  -- grade C
    postcode               VARCHAR(10) NOT NULL   -- grade C
);

-- Address: no attributes in evidence yet (grade C); see U-11
