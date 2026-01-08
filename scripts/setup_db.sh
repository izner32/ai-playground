#!/bin/bash

set -e

PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project)}
INSTANCE_NAME=${DB_INSTANCE_NAME:-""}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID is not set"
    exit 1
fi

if [ -z "$INSTANCE_NAME" ]; then
    echo "Error: DB_INSTANCE_NAME is not set"
    echo "Get it from: terraform output database_instance_name"
    exit 1
fi

echo "====================================="
echo "Database Setup Script"
echo "====================================="
echo "Project: $PROJECT_ID"
echo "Instance: $INSTANCE_NAME"
echo "====================================="

echo "Creating sample tables..."

SQL_SCRIPT=$(cat <<'EOF'
-- Create sample users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Create sample products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    stock_quantity INTEGER DEFAULT 0,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sample orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total_amount DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email, last_login) VALUES
    ('john_doe', 'john@example.com', NOW() - INTERVAL '2 days'),
    ('jane_smith', 'jane@example.com', NOW() - INTERVAL '1 day'),
    ('bob_wilson', 'bob@example.com', NOW())
ON CONFLICT (username) DO NOTHING;

INSERT INTO products (name, description, price, stock_quantity, category) VALUES
    ('Laptop', 'High-performance laptop', 1299.99, 50, 'Electronics'),
    ('Mouse', 'Wireless mouse', 29.99, 200, 'Electronics'),
    ('Desk Chair', 'Ergonomic office chair', 249.99, 30, 'Furniture'),
    ('Monitor', '27-inch 4K monitor', 399.99, 75, 'Electronics')
ON CONFLICT DO NOTHING;

INSERT INTO orders (user_id, total_amount, status) VALUES
    (1, 1329.98, 'completed'),
    (2, 249.99, 'pending'),
    (1, 29.99, 'completed')
ON CONFLICT DO NOTHING;

SELECT 'Database setup completed!' as message;
EOF
)

DB_USER=${DB_USER:-"aiagent"}
DB_NAME=${DB_NAME:-"aiagent"}

echo "$SQL_SCRIPT" | gcloud sql connect "$INSTANCE_NAME" --user="$DB_USER" --database="$DB_NAME" --quiet

echo ""
echo "====================================="
echo "Database setup completed!"
echo "====================================="
echo "Tables created:"
echo "  - users"
echo "  - products"
echo "  - orders"
echo ""
echo "Sample data inserted successfully"
