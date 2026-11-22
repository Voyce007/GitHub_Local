-- STAND-IN schema for FinCore, generated from evidence batch loop-01.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-07 LegalEntity · grade C · approved (provisional) — simulated
CREATE TABLE legal_entity (
    legal_entity_code      CHAR(6),  -- grade C
    registered_name        VARCHAR(200) NOT NULL,  -- grade C
    country_code           CHAR(2) NOT NULL,  -- grade C
    functional_currency    CHAR(3) NOT NULL,  -- grade C
    PRIMARY KEY (legal_entity_code)
);

-- ENT-08 CostCentre · grade C · approved (provisional) — simulated
CREATE TABLE cost_centre (
    cost_centre_code       VARCHAR(10),  -- grade C
    name                   VARCHAR(100) NOT NULL,  -- grade C
    legal_entity_code      CHAR(6) NOT NULL,  -- grade C
    PRIMARY KEY (cost_centre_code)
);

-- ENT-09 Account · grade C · approved (provisional) — simulated
CREATE TABLE account (
    account_code           VARCHAR(10),  -- grade C
    account_name           VARCHAR(100) NOT NULL,  -- grade C
    account_type           VARCHAR(10) NOT NULL,  -- grade C
    PRIMARY KEY (account_code)
);

-- ENT-10 Invoice · grade C · approved (provisional) — simulated
CREATE TABLE invoice (
    invoice_number         VARCHAR(12),  -- grade C
    customer_number        CHAR(10) NOT NULL,  -- grade C
    legal_entity_code      CHAR(6) NOT NULL,  -- grade C
    invoice_date           DATE NOT NULL,  -- grade C
    due_date               DATE NOT NULL,  -- grade C
    total_amount           NUMERIC(18,2) NOT NULL,  -- grade C
    amount_outstanding     NUMERIC(18,2) NOT NULL,  -- grade C
    currency               CHAR(3) NOT NULL,  -- grade C
    PRIMARY KEY (invoice_number)
);

-- ENT-11 CustomerEntity · grade C · approved (provisional) — simulated
CREATE TABLE customer_entity (
    customer_number        CHAR(10) NOT NULL,  -- grade C
    legal_entity_code      CHAR(6) NOT NULL,  -- grade C
    credit_limit           NUMERIC(18,2)   -- grade C
);
