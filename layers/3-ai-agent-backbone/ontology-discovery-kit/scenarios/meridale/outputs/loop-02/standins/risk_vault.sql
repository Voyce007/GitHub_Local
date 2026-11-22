-- STAND-IN schema for RiskVault, generated from evidence batch loop-02.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-05 Risk · grade C · approved (provisional) — simulated
CREATE TABLE risk (
    risk_id                VARCHAR(12) NOT NULL,  -- grade C
    title                  VARCHAR(200) NOT NULL,  -- grade C
    rating                 VARCHAR(20) NOT NULL CHECK (rating IN ('LOW', 'MEDIUM', 'HIGH')),  -- grade C; RiskRating grade B
    cost_centre_code       VARCHAR(10) NOT NULL,  -- grade C
    customer_number        CHAR(10),  -- grade C
    review_date            DATE,  -- grade C
    PRIMARY KEY (risk_id)
);

-- ENT-06 Control · grade C · approved (provisional) — simulated
CREATE TABLE control (
    control_id             VARCHAR(12) NOT NULL,  -- grade C
    risk_id                VARCHAR(12) NOT NULL,  -- grade C
    control_type           VARCHAR(20) NOT NULL CHECK (control_type IN ('PREVENTIVE', 'DETECTIVE')),  -- grade C; ControlType grade B
    last_tested            DATE,  -- grade C
    PRIMARY KEY (control_id)
);
