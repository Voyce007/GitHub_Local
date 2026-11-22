-- Example DDL extract shared by the LedgerOne (Finance systems) team (2023). Partial.
CREATE TABLE legal_entity (
    legal_entity_code   CHAR(6)        PRIMARY KEY,
    registered_name     VARCHAR(200)   NOT NULL,
    country_code        CHAR(2)        NOT NULL,
    functional_currency CHAR(3)        NOT NULL
);

CREATE TABLE cost_centre (
    cost_centre_code    VARCHAR(10)    PRIMARY KEY,
    name                VARCHAR(100)   NOT NULL,
    legal_entity_code   CHAR(6)        NOT NULL REFERENCES legal_entity(legal_entity_code)
);

CREATE TABLE account (
    account_code        VARCHAR(10)    PRIMARY KEY,
    account_name        VARCHAR(100)   NOT NULL,
    account_type        VARCHAR(10)    NOT NULL
);

CREATE TABLE invoice (
    invoice_number      VARCHAR(12)    PRIMARY KEY,
    customer_no         CHAR(10)       NOT NULL,
    legal_entity_code   CHAR(6)        NOT NULL REFERENCES legal_entity(legal_entity_code),
    invoice_date        DATE           NOT NULL,
    total_amount        NUMERIC(18,2)  NOT NULL,
    currency            CHAR(3)        NOT NULL
);

CREATE TABLE customer_entity (
    customer_no         CHAR(10)       NOT NULL,
    legal_entity_code   CHAR(6)        NOT NULL REFERENCES legal_entity(legal_entity_code),
    PRIMARY KEY (customer_no, legal_entity_code)
);
