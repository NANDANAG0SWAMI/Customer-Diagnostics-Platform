-- This script will be run the first time the diagnostics database is created.

-- Create a table to store the results of our diagnostic reports
CREATE TABLE diagnosis_reports (
    report_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    summary TEXT,
    raw_data JSONB, -- Using JSONB is efficient for storing and querying JSON data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- You could add some sample initial data here if needed, for example:
-- INSERT INTO diagnosis_reports (product_id, product_name, summary, raw_data) VALUES 
-- (101, 'Quantum Laptop', 'Initial system check.', '{}');
