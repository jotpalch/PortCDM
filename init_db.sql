-- Create ship_berth_order table
CREATE TABLE IF NOT EXISTS ship_berth_order (
    berth_number VARCHAR(10),
    berthing_time VARCHAR(20),
    status VARCHAR(10),
    pilotage_time VARCHAR(20),
    ship_name_chinese VARCHAR(50),
    ship_name_english VARCHAR(50),
    port_agent VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ship_status table
CREATE TABLE IF NOT EXISTS ship_status (
    ship_voyage_number VARCHAR(10) PRIMARY KEY,
    ship_name VARCHAR(100),
    latest_event VARCHAR(100),
    port_entry_application VARCHAR(10),
    berth_shift_application VARCHAR(10),
    port_departure_application VARCHAR(10),
    offshore_vessel_entry VARCHAR(10),
    at_anchor VARCHAR(10),
    port_entry_in_progress VARCHAR(10),
    loading_unloading_notice VARCHAR(10),
    berth_shift_in_progress VARCHAR(10),
    berth_shift_loading_unloading VARCHAR(10),
    port_departure_in_progress VARCHAR(10),
    vessel_departed VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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