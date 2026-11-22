-- Schema export from the TradeDesk production database (structure only, no data). 2026-12-01.
CREATE TABLE customer (
    customer_no      CHAR(10)       PRIMARY KEY,
    cust_type        CHAR(3)        NOT NULL,
    full_name        VARCHAR(200)   NOT NULL,
    reg_number       VARCHAR(20),
    credit_status    CHAR(3)        NOT NULL,
    credit_limit     NUMERIC(18,2),
    created_ts       TIMESTAMP      NOT NULL,
    updated_ts       TIMESTAMP      NOT NULL
);

CREATE TABLE customer_address (
    customer_no      CHAR(10)       NOT NULL REFERENCES customer(customer_no),
    addr_type        CHAR(3)        NOT NULL,
    line_1           VARCHAR(100)   NOT NULL,
    line_2           VARCHAR(100),
    postcode         VARCHAR(10)    NOT NULL,
    country_code     CHAR(2)        NOT NULL,
    PRIMARY KEY (customer_no, addr_type)
);
