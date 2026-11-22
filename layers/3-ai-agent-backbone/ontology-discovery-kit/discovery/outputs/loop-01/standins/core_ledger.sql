-- STAND-IN schema for CoreLedger, generated from evidence batch loop-01.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-03 Account · grade C · approved (provisional) — simulated
CREATE TABLE account (
    account_number         CHAR(8),  -- grade C
    sort_code              CHAR(6) NOT NULL,  -- grade C
    product_code           VARCHAR(10) NOT NULL,  -- grade C
    currency               CHAR(3) NOT NULL,  -- grade C
    status                 VARCHAR(10) NOT NULL,  -- grade C
    opened_date            DATE NOT NULL,  -- grade C
    PRIMARY KEY (account_number)
);

-- ENT-04 AccountHolder · grade C · approved (provisional) — simulated
CREATE TABLE account_holder (
    account_number         CHAR(8) NOT NULL,  -- grade C
    customer_number        CHAR(10) NOT NULL,  -- grade C
    holder_role            VARCHAR(10) NOT NULL   -- grade C
);
