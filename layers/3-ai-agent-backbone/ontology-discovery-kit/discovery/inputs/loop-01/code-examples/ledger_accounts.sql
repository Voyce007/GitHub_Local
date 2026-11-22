-- Example DDL extract shared by the CoreLedger team (2023). Partial.
CREATE TABLE account (
    account_number   CHAR(8)      PRIMARY KEY,
    sort_code        CHAR(6)      NOT NULL,
    product_code     VARCHAR(10)  NOT NULL,
    currency         CHAR(3)      NOT NULL DEFAULT 'GBP',
    status           VARCHAR(10)  NOT NULL,
    opened_date      DATE         NOT NULL
);

CREATE TABLE account_holder (
    account_number   CHAR(8)      NOT NULL REFERENCES account(account_number),
    customer_no      CHAR(10)     NOT NULL,
    holder_role      VARCHAR(10)  NOT NULL,
    PRIMARY KEY (account_number, customer_no)
);
