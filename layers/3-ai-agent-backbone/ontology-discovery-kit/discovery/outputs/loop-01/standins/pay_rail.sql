-- STAND-IN schema for PayRail, generated from evidence batch loop-01.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-06 PaymentInstruction · grade C · approved (provisional) — simulated
CREATE TABLE payment_instruction (
    payment_id             VARCHAR(255),  -- grade C
    debit_account_number   VARCHAR(255),  -- grade C
    amount                 NUMERIC(18,2),  -- grade C
    currency               VARCHAR(255),  -- grade C
    status                 VARCHAR(20)   -- grade C; PaymentStatus grade X — values contested
);
