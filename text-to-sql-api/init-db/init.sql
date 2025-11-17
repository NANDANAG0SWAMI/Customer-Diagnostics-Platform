-- Create Customers Table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    join_date DATE
);

-- Create Products Table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price NUMERIC(10, 2)
);

-- Create Support Tickets Table
CREATE TABLE support_tickets (
    ticket_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    product_id INT REFERENCES products(product_id),
    subject VARCHAR(255),
    description TEXT,
    status VARCHAR(20) CHECK (status IN ('open', 'in_progress', 'closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Sample Data
INSERT INTO customers (first_name, last_name, email, join_date) VALUES
('Alice', 'Johnson', 'alice.j@example.com', '2023-01-15'),
('Bob', 'Smith', 'bob.smith@example.com', '2023-02-20'),
('Charlie', 'Brown', 'charlie.b@example.com', '2023-03-05');

INSERT INTO products (product_name, category, price) VALUES
('Quantum Laptop', 'Electronics', 1200.00),
('DataStream Router', 'Networking', 80.00),
('Cloud-Sync Hard Drive', 'Storage', 150.00);

INSERT INTO support_tickets (customer_id, product_id, subject, description, status) VALUES
(1, 1, 'Laptop screen flickering', 'My new Quantum Laptop screen has started to flicker intermittently.', 'open'),
(2, 2, 'Cannot connect to Wi-Fi', 'My DataStream Router is not broadcasting a Wi-Fi signal.', 'in_progress'),
(1, 3, 'Drive not recognized', 'The Cloud-Sync Hard Drive is not showing up on my computer.', 'closed');

