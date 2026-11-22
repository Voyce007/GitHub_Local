-- STAND-IN schema for ShopFront, generated from evidence batch loop-01.
-- This is a hypothesis for the proof of concept, not a copy of the real system.
-- Each column comment carries its evidence grade. Replace with the real schema when it arrives.

-- ENT-13 OrderRequest · grade C · approved (provisional) — simulated
CREATE TABLE order_request (
    order_id               VARCHAR(255),  -- grade C
    customer_number        VARCHAR(255),  -- grade C
    currency               VARCHAR(255),  -- grade C
    total_amount           NUMERIC(18,2),  -- grade C
    status                 VARCHAR(20)   -- grade C; OrderStatus grade X — values contested
);

-- OrderLine: no attributes in evidence yet (grade C); see U-13
