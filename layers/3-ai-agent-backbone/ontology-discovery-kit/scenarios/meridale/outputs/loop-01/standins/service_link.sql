-- STAND-IN schema for ServiceLink, generated from evidence batch loop-01.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-03 Client · grade C · approved (provisional) — simulated
CREATE TABLE client (
    client_ref             VARCHAR(12) NOT NULL,  -- grade C
    customer_number        CHAR(10),  -- grade C
    client_name            VARCHAR(200) NOT NULL,  -- grade C
    credit_limit           NUMERIC(18,2),  -- grade C
    PRIMARY KEY (client_ref)
);

-- ENT-04 ServiceContract · grade C · approved (provisional) — simulated
CREATE TABLE service_contract (
    contract_id            VARCHAR(12) NOT NULL,  -- grade C
    client_ref             VARCHAR(12) NOT NULL,  -- grade C
    start_date             DATE NOT NULL,  -- grade C
    end_date               DATE,  -- grade C
    annual_value           NUMERIC(18,2) NOT NULL,  -- grade C
    PRIMARY KEY (contract_id)
);
