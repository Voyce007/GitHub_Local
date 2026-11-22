-- STAND-IN schema for CustHub, generated from evidence batch loop-01.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-01 Customer · grade B · approved (provisional) — simulated
CREATE TABLE customer (
    customer_number        CHAR(10) NOT NULL,  -- grade B
    customer_type          VARCHAR(20) NOT NULL,  -- grade B; CustomerType grade X — values contested
    full_name              VARCHAR(200) NOT NULL,  -- grade B
    date_of_birth          DATE,  -- grade B
    email_address          VARCHAR(254),  -- grade B
    kyc_status             VARCHAR(20) NOT NULL CHECK (kyc_status IN ('PENDING', 'PASSED', 'FAILED', 'REFERRED')),  -- grade B; KycStatus grade B
    created_timestamp      TIMESTAMP NOT NULL,  -- grade C
    PRIMARY KEY (customer_number)
);

-- ENT-02 CustomerAddress · grade C · approved (provisional) — simulated
CREATE TABLE customer_address (
    customer_number        CHAR(10) NOT NULL,  -- grade C
    address_type           VARCHAR(20) NOT NULL CHECK (address_type IN ('HOME', 'CORRESPONDENCE')),  -- grade C; AddressType grade C
    line1                  VARCHAR(100) NOT NULL,  -- grade C
    postcode               VARCHAR(10) NOT NULL   -- grade C
);

-- Address: no attributes in evidence yet (grade C); see U-08
