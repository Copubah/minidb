# MiniDB - A Simple Relational Database Management System

A lightweight RDBMS built from scratch in Python, featuring SQL parsing, indexing, and CRUD operations.

## Overview

MiniDB is a complete relational database management system implemented from the ground up without using any existing database libraries. It demonstrates core database concepts including SQL parsing, B-Tree indexing, query optimization, and transaction processing.

## Features

### SQL Support
- CREATE TABLE with column constraints
- INSERT, SELECT, UPDATE, DELETE operations
- DROP TABLE functionality
- WHERE clauses with AND/OR logic
- INNER JOIN operations
- ORDER BY and LIMIT clauses

### Data Types
- INTEGER: Whole numbers
- TEXT: Variable-length strings
- FLOAT: Decimal numbers
- BOOLEAN: True/false values

### Constraints
- PRIMARY KEY: Unique identifier with automatic indexing
- UNIQUE: Ensures column values are unique
- NOT NULL: Prevents null values

### Performance Features
- B-Tree indexing for O(log n) lookups on indexed columns
- Query optimization using indexes when available
- Efficient join algorithms

### Storage
- JSON-based persistence for human-readable data files
- Automatic schema validation
- Crash-safe writes

### Interface
- Interactive REPL with command history
- SQL console with syntax highlighting
- Web-based demo application

## Installation

```bash
cd minidb
pip install -r requirements.txt
```

## Quick Start

### 1. REPL Mode

Launch the interactive database shell:

```bash
python -m minidb.repl
```

### 2. Create Your First Table

```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    salary FLOAT,
    active BOOLEAN
);
```

### 3. Insert Data

```sql
INSERT INTO employees (id, name, email, salary, active) 
VALUES (1, 'Alice Johnson', 'alice@company.com', 75000.0, true);

INSERT INTO employees (id, name, email, salary, active) 
VALUES (2, 'Bob Smith', 'bob@company.com', 68000.0, true);
```

### 4. Query Data

```sql
-- Select all employees
SELECT * FROM employees;

-- Find high earners
SELECT name, salary FROM employees WHERE salary > 70000;

-- Order by salary
SELECT * FROM employees ORDER BY salary DESC;
```

## Usage Examples

### Basic Operations

```sql
-- Create a table with constraints
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price FLOAT,
    category TEXT
);

-- Insert multiple records
INSERT INTO products (id, name, price, category) VALUES (1, 'Laptop', 999.99, 'Electronics');
INSERT INTO products (id, name, price, category) VALUES (2, 'Book', 19.99, 'Education');

-- Update records
UPDATE products SET price = 899.99 WHERE id = 1;

-- Delete records
DELETE FROM products WHERE category = 'Education';
```

### Advanced Queries

```sql
-- Create related tables
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    product_id INTEGER,
    quantity INTEGER
);

-- Join tables
SELECT employees.name, products.name, orders.quantity 
FROM employees 
JOIN orders ON employees.id = orders.employee_id
JOIN products ON products.id = orders.product_id;

-- Complex WHERE conditions
SELECT * FROM employees 
WHERE salary > 60000 AND active = true 
ORDER BY salary DESC 
LIMIT 5;
```

## Web Application Demo

MiniDB includes a complete web application demonstrating real-world usage:

```bash
python app.py
```

Then visit http://localhost:5000

The demo app is a task manager featuring:
- Create, read, update, delete tasks
- Priority levels and status tracking
- Live SQL console for direct database queries
- Responsive web interface

## Architecture

### Core Components

#### engine.py - Database Engine
- Table and column management
- Row storage and retrieval
- Index management
- Constraint validation
- Transaction handling

#### parser.py - SQL Parser
- Tokenization of SQL statements
- Abstract syntax tree generation
- Support for complex expressions
- Error handling and reporting

#### executor.py - Query Executor
- Query plan generation
- Index utilization
- Join algorithms
- Result formatting

#### btree.py - B-Tree Index
- Self-balancing tree structure
- O(log n) search, insert, delete
- Range queries
- Duplicate key handling

#### repl.py - Interactive Shell
- Command-line interface
- SQL history
- Meta-commands (.tables, .schema)
- Error reporting

### Design Decisions

#### Storage Format
JSON was chosen for persistence to maintain human readability and simplicity. In a production system, a binary format would be more efficient.

#### Indexing Strategy
B-Trees provide excellent performance for both equality and range queries. Primary keys and unique columns are automatically indexed.

#### Query Processing
The system uses a simple but effective query processing pipeline:
1. Parse SQL into AST
2. Generate execution plan
3. Utilize indexes when possible
4. Execute and return results

## Performance Characteristics

- Table scans: O(n) where n is number of rows
- Indexed lookups: O(log n) where n is number of indexed values
- Joins: O(n * m) for nested loop joins
- Memory usage: Entire database loaded into memory

## Limitations

- No concurrent access (single-threaded)
- No transactions or ACID guarantees
- Limited SQL feature set
- In-memory storage only
- No query optimization beyond index usage

## Testing

Run the test suite:

```bash
python -c "
from minidb.engine import Database
from minidb.executor import Executor

# Test basic operations
db = Database()
ex = Executor(db)

# Create and populate test data
ex.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
ex.execute(\"INSERT INTO test VALUES (1, 'Alice')\")
result = ex.execute('SELECT * FROM test')
print('Test passed!' if result.rows else 'Test failed!')
"
```

## REPL Commands

The interactive shell supports several meta-commands:

```
.help          Show help information
.tables        List all tables in the database
.schema TABLE  Show the schema for a specific table
.quit          Exit the REPL
```

## SQL Syntax Reference

### Data Definition Language (DDL)

```sql
-- Create table
CREATE TABLE table_name (
    column_name TYPE [PRIMARY KEY] [UNIQUE] [NOT NULL],
    ...
);

-- Drop table
DROP TABLE table_name;
```

### Data Manipulation Language (DML)

```sql
-- Insert data
INSERT INTO table_name (col1, col2) VALUES (val1, val2);

-- Select data
SELECT col1, col2 FROM table_name 
[WHERE condition] 
[ORDER BY column [ASC|DESC]] 
[LIMIT number];

-- Update data
UPDATE table_name SET col1 = val1 [WHERE condition];

-- Delete data
DELETE FROM table_name [WHERE condition];

-- Join tables
SELECT t1.col1, t2.col2 
FROM table1 t1 
JOIN table2 t2 ON t1.id = t2.foreign_id;
```

## Contributing

This project was built as a coding challenge to demonstrate database internals knowledge. Key areas for enhancement:

1. Concurrency control and locking
2. Write-ahead logging for durability
3. Query optimization and cost-based planning
4. Additional SQL features (GROUP BY, subqueries, etc.)
5. Network protocol for client-server architecture

## Credits

Built from scratch as a coding challenge submission. No external database libraries used.

The implementation demonstrates understanding of:
- Database storage engines
- SQL parsing and execution
- Index data structures
- Query processing algorithms
- Database system architecture

## License

This project is provided as-is for educational and demonstration purposes.
