-- Create ship_status table
CREATE TABLE IF NOT EXISTS ship_status (
    ship_voyage_number VARCHAR(10) PRIMARY KEY,
    ship_name VARCHAR(100),
    latest_event VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ship_berth_order table
CREATE TABLE IF NOT EXISTS ship_berth_order (
    berth_number VARCHAR(10),
    berthing_time VARCHAR(20),
    status VARCHAR(10),
    pilotage_time VARCHAR(20),
    ship_name_chinese VARCHAR(50),
    ship_name_english VARCHAR(50),
    port_agent VARCHAR(50),
    PRIMARY KEY (berth_number, ship_name_english)
);

-- Create ship_voyage table
CREATE TABLE IF NOT EXISTS ship_voyage (
    ship_voyage_number VARCHAR(10) PRIMARY KEY,
    pass_10_miles_time VARCHAR(20),
    pass_5_miles_time VARCHAR(20)
);

-- Create ship_events table
CREATE TABLE IF NOT EXISTS ship_events (
    id SERIAL PRIMARY KEY,
    ship_voyage_number VARCHAR(10),
    event_source VARCHAR(50),
    event_time TIMESTAMP,
    event_name VARCHAR(100),
    navigation_status VARCHAR(50),
    pilot_order_number VARCHAR(20),
    berth_code VARCHAR(10),
    event_content TEXT,
    UNIQUE (ship_voyage_number, event_time, event_name)
);

-- Create the trigger function
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger for ship_status table
CREATE TRIGGER update_ship_status_timestamp
BEFORE UPDATE ON ship_status
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Create the trigger for ship_berth_order table
CREATE TRIGGER update_ship_berth_order_timestamp
BEFORE UPDATE ON ship_berth_order
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();