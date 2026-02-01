CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS ix_user_email ON "user" (email);
CREATE INDEX IF NOT EXISTS ix_user_id ON "user" (id);
CREATE INDEX IF NOT EXISTS ix_user_uuid ON "user" (uuid);

CREATE TABLE IF NOT EXISTS "event" (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    type VARCHAR(255),
    title VARCHAR(255),
    description VARCHAR(255),
    owner_id INTEGER REFERENCES "user"(id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'SCHEDULED',
    location VARCHAR(255),
    available_number_of_tickets INTEGER
);

CREATE INDEX IF NOT EXISTS ix_event_id ON "event" (id);
CREATE INDEX IF NOT EXISTS ix_event_uuid ON "event" (uuid);
CREATE INDEX IF NOT EXISTS ix_event_type ON "event" (type);
CREATE INDEX IF NOT EXISTS ix_event_title ON "event" (title);
CREATE INDEX IF NOT EXISTS ix_event_start_date ON "event" (start_date);
CREATE INDEX IF NOT EXISTS ix_event_end_date ON "event" (end_date);
CREATE INDEX IF NOT EXISTS ix_event_location ON "event" (location);

CREATE TABLE IF NOT EXISTS "order" (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    owner_id INTEGER REFERENCES "user"(id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'open',
    event_id INTEGER REFERENCES "event"(id),
    number_of_tickets INTEGER
);

CREATE INDEX IF NOT EXISTS ix_order_id ON "order" (id);
CREATE INDEX IF NOT EXISTS ix_order_uuid ON "order" (uuid);

CREATE TABLE IF NOT EXISTS "ticket" (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'open',
    event_id INTEGER REFERENCES "event"(id),
    order_id INTEGER REFERENCES "order"(id)
);

CREATE INDEX IF NOT EXISTS ix_ticket_id ON "ticket" (id);
CREATE INDEX IF NOT EXISTS ix_ticket_uuid ON "ticket" (uuid);
