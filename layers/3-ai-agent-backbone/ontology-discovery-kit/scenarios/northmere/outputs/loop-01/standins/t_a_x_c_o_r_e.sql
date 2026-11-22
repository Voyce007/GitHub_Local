-- STAND-IN schema for TAXCORE, generated from evidence batch loop-01.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-01 Person · grade C · approved (provisional) — simulated
CREATE TABLE person (
    person_id              INTEGER NOT NULL,  -- grade C
    ni_number              CHAR(9),  -- grade C
    forename               VARCHAR(60) NOT NULL,  -- grade C
    surname                VARCHAR(60) NOT NULL,  -- grade C
    date_of_birth          DATE NOT NULL,  -- grade C
    date_of_death          DATE,  -- grade C
    corr_pref              VARCHAR(20) NOT NULL CHECK (corr_pref IN ('POST', 'DIGITAL')),  -- grade C; CorrespondencePreference grade C
    PRIMARY KEY (person_id)
);

-- ENT-02 Address · grade C · approved (provisional) — simulated
CREATE TABLE address (
    person_id              INTEGER NOT NULL,  -- grade C
    address_type           VARCHAR(20) NOT NULL CHECK (address_type IN ('RESIDENTIAL', 'CORRESPONDENCE')),  -- grade C; AddressType grade C
    line1                  VARCHAR(100) NOT NULL,  -- grade C
    postcode               VARCHAR(10) NOT NULL   -- grade C
);

-- ENT-03 Employer · grade C · approved (provisional) — simulated
CREATE TABLE employer (
    employer_ref           VARCHAR(12) NOT NULL,  -- grade C
    employer_name          VARCHAR(200) NOT NULL,  -- grade C
    PRIMARY KEY (employer_ref)
);

-- ENT-04 Employment · grade C · approved (provisional) — simulated
CREATE TABLE employment (
    employment_id          INTEGER NOT NULL,  -- grade C
    person_id              INTEGER NOT NULL,  -- grade C
    employer_ref           VARCHAR(12) NOT NULL,  -- grade C
    start_date             DATE NOT NULL,  -- grade C
    end_date               DATE,  -- grade C
    status                 VARCHAR(20) NOT NULL,  -- grade C; EmploymentStatus grade X — values contested
    PRIMARY KEY (employment_id)
);

-- ENT-05 TaxCode · grade C · approved (provisional) — simulated
CREATE TABLE tax_code (
    employment_id          INTEGER NOT NULL,  -- grade C
    tax_code               VARCHAR(8) NOT NULL,  -- grade C
    effective_from         DATE NOT NULL   -- grade C
);

-- ENT-06 PayPeriod · grade C · approved (provisional) — simulated
CREATE TABLE pay_period (
    employment_id          INTEGER NOT NULL,  -- grade C
    tax_year               CHAR(7) NOT NULL,  -- grade C
    period_number          SMALLINT NOT NULL,  -- grade C
    gross_pay              DECIMAL(11,2) NOT NULL,  -- grade C
    tax_deducted           DECIMAL(11,2) NOT NULL,  -- grade C
    ni_category            CHAR(1) NOT NULL   -- grade C
);

-- ENT-07 NiContribution · grade C · approved (provisional) — simulated
CREATE TABLE ni_contribution (
    employment_id          INTEGER NOT NULL,  -- grade C
    tax_year               CHAR(7) NOT NULL,  -- grade C
    period_number          SMALLINT NOT NULL,  -- grade C
    ni_category            VARCHAR(20) NOT NULL,  -- grade C; NiCategory grade X — values contested
    employee_nic           DECIMAL(11,2) NOT NULL,  -- grade C
    employer_nic           DECIMAL(11,2) NOT NULL   -- grade C
);

-- ENT-08 NiRecord · grade C · approved (provisional) — simulated
CREATE TABLE ni_record (
    person_id              INTEGER NOT NULL,  -- grade C
    tax_year               CHAR(7) NOT NULL,  -- grade C
    qualifying             VARCHAR(20) NOT NULL CHECK (qualifying IN ('YES', 'NO')),  -- grade C; QualifyingYear grade C
    class1_total           DECIMAL(11,2) NOT NULL   -- grade C
);

-- ENT-09 ChildcareAccount · grade C · approved (provisional) — simulated
CREATE TABLE childcare_account (
    cc_account_id          INTEGER NOT NULL,  -- grade C
    person_id              INTEGER NOT NULL,  -- grade C
    status                 VARCHAR(20) NOT NULL CHECK (status IN ('OPEN', 'SUSPENDED', 'CLOSED')),  -- grade C; ChildcareAccountStatus grade B
    opened_date            DATE NOT NULL,  -- grade C
    PRIMARY KEY (cc_account_id)
);

-- ENT-10 Child · grade C · approved (provisional) — simulated
CREATE TABLE child (
    child_id               INTEGER NOT NULL,  -- grade C
    cc_account_id          INTEGER NOT NULL,  -- grade C
    person_id              INTEGER,  -- grade C
    forename               VARCHAR(60) NOT NULL,  -- grade C
    date_of_birth          DATE NOT NULL,  -- grade C
    PRIMARY KEY (child_id)
);

-- ENT-11 ChildcarePayment · grade C · approved (provisional) — simulated
CREATE TABLE childcare_payment (
    payment_id             INTEGER NOT NULL,  -- grade C
    cc_account_id          INTEGER NOT NULL,  -- grade C
    provider_ref           VARCHAR(12) NOT NULL,  -- grade C
    parent_amount          DECIMAL(9,2) NOT NULL,  -- grade C
    topup_amount           DECIMAL(9,2),  -- grade C
    paid_date              DATE NOT NULL,  -- grade C
    PRIMARY KEY (payment_id)
);

-- ENT-12 EligibilityCheck · grade C · approved (provisional) — simulated
CREATE TABLE eligibility_check (
    check_id               INTEGER NOT NULL,  -- grade C
    cc_account_id          INTEGER NOT NULL,  -- grade C
    check_date             DATE NOT NULL,  -- grade C
    expected_income        DECIMAL(11,2) NOT NULL,  -- grade C
    outcome                VARCHAR(20) NOT NULL CHECK (outcome IN ('ELIGIBLE', 'NOT_ELIGIBLE')),  -- grade C; EligibilityOutcome grade C
    PRIMARY KEY (check_id)
);
