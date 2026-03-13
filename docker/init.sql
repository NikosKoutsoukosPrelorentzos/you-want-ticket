DROP TABLE IF EXISTS "ticket";
DROP TABLE IF EXISTS "order";
DROP TABLE IF EXISTS "event";
DROP TABLE IF EXISTS "place";
DROP TABLE IF EXISTS "user";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    user_role VARCHAR(50) DEFAULT 'CUSTOMER'
);

CREATE INDEX IF NOT EXISTS ix_user_email ON "user" (email);
CREATE INDEX IF NOT EXISTS ix_user_id ON "user" (id);
CREATE INDEX IF NOT EXISTS ix_user_uuid ON "user" (uuid);

CREATE TABLE IF NOT EXISTS "place" (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    owner_uuid UUID REFERENCES "user"(uuid),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    capacity INTEGER
);

CREATE INDEX IF NOT EXISTS ix_place_id ON "place" (id);
CREATE INDEX IF NOT EXISTS ix_place_uuid ON "place" (uuid);
CREATE INDEX IF NOT EXISTS ix_place_name ON "place" (name);
CREATE INDEX IF NOT EXISTS ix_place_owner_uuid ON "place" (owner_uuid);

CREATE TABLE IF NOT EXISTS "event" (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    type VARCHAR(255),
    title VARCHAR(255),
    description VARCHAR(255),
    owner_uuid UUID REFERENCES "user"(uuid),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'SCHEDULED',
    location VARCHAR(255),
    place_uuid UUID REFERENCES "place"(uuid),
    available_number_of_tickets INTEGER
);

CREATE INDEX IF NOT EXISTS ix_event_id ON "event" (id);
CREATE INDEX IF NOT EXISTS ix_event_uuid ON "event" (uuid);
CREATE INDEX IF NOT EXISTS ix_event_type ON "event" (type);
CREATE INDEX IF NOT EXISTS ix_event_title ON "event" (title);
CREATE INDEX IF NOT EXISTS ix_event_start_date ON "event" (start_date);
CREATE INDEX IF NOT EXISTS ix_event_end_date ON "event" (end_date);
CREATE INDEX IF NOT EXISTS ix_event_location ON "event" (location);
CREATE INDEX IF NOT EXISTS ix_event_place_uuid ON "event" (place_uuid);

CREATE TABLE IF NOT EXISTS "order" (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    owner_uuid UUID REFERENCES "user"(uuid),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'IN_PROGRESS',
    event_uuid UUID REFERENCES "event"(uuid),
    number_of_tickets INTEGER
);

CREATE INDEX IF NOT EXISTS ix_order_id ON "order" (id);
CREATE INDEX IF NOT EXISTS ix_order_uuid ON "order" (uuid);

CREATE TABLE IF NOT EXISTS "ticket" (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'SCHEDULED',
    event_uuid UUID REFERENCES "event"(uuid),
    order_uuid UUID REFERENCES "order"(uuid),
    owner_uuid UUID REFERENCES "user"(uuid)
);

CREATE INDEX IF NOT EXISTS ix_ticket_id ON "ticket" (id);
CREATE INDEX IF NOT EXISTS ix_ticket_uuid ON "ticket" (uuid);
