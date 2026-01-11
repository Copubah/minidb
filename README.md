# MiniDB - A Simple Relational Database Management System

MiniDB is a complete relational database management system built from scratch in Python to demonstrate core database concepts and system design skills. This project implements SQL parsing, B-Tree indexing, query optimization, and CRUD operations without using any existing database libraries. It showcases understanding of database internals, data structures, and software architecture through a working system that includes both a command-line interface and a web application demo.

Built as a coding challenge submission, MiniDB proves that complex systems can be constructed with clean, maintainable code while providing real functionality that users can interact with immediately.

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

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Copubah/minidb.git
   cd minidb
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Start the interactive shell
   ```bash
   python -m minidb.repl
   ```

### Your First Database

Once in the MiniDB shell, try these commands:

```sql
-- Create a table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    age INTEGER
);

-- Insert some data
INSERT INTO users (id, name, email, age) VALUES (1, 'Alice Johnson', 'alice@example.com', 28);
INSERT INTO users (id, name, email, age) VALUES (2, 'Bob Smith', 'bob@example.com', 34);
INSERT INTO users (id, name, email, age) VALUES (3, 'Carol Davis', 'carol@example.com', 25);

-- Query the data
SELECT * FROM users;
SELECT name, age FROM users WHERE age > 25;
SELECT * FROM users ORDER BY age DESC;

-- Update records
UPDATE users SET age = 29 WHERE name = 'Alice Johnson';

-- Join with another table
CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, product TEXT, amount FLOAT);
INSERT INTO orders (id, user_id, product, amount) VALUES (1, 1, 'Laptop', 999.99);
INSERT INTO orders (id, user_id, product, amount) VALUES (2, 2, 'Mouse', 29.99);

SELECT users.name, orders.product, orders.amount 
FROM users 
JOIN orders ON users.id = orders.user_id;
```

### Try the Web Demo

Launch the web application to see MiniDB in action:

```bash
python app.py
```

Then open http://localhost:5000 in your browser to use the task management demo with a live SQL console.

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

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                           MiniDB Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │    REPL     │    │  Web App    │    │   Direct API        │  │
│  │   (CLI)     │    │  (Flask)    │    │   Integration       │  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────────────┘  │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│  ┌─────────────────────────▼─────────────────────────────────┐  │
│  │                   SQL Executor                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │  │   Parser    │  │  Planner    │  │   Executor      │   │  │
│  │  │ (Tokenizer, │  │ (Index      │  │ (Join, Filter,  │   │  │
│  │  │  AST Gen)   │  │  Selection) │  │  Projection)    │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │                                    │
│  ┌─────────────────────────▼─────────────────────────────────┐  │
│  │                 Database Engine                           │  │
│  │                                                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │  │   Tables    │  │   Indexes   │  │   Constraints   │   │  │
│  │  │             │  │             │  │                 │   │  │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────────┐ │   │  │
│  │  │ │ Schema  │ │  │ │ B-Tree  │ │  │ │ Primary Key │ │   │  │
│  │  │ │ Columns │ │  │ │ Nodes   │ │  │ │ Unique      │ │   │  │
│  │  │ │ Rows    │ │  │ │ Keys    │ │  │ │ Not Null    │ │   │  │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────────┘ │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │  │
│  └─────────────────────────┬─────────────────────────────────┘  │
│                            │                                    │
│  ┌─────────────────────────▼─────────────────────────────────┐  │
│  │                 Storage Layer                             │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │              JSON Persistence                       │ │  │
│  │  │                                                     │ │  │
│  │  │  ┌─────────────┐    ┌─────────────────────────────┐ │ │  │
│  │  │  │   Schema    │    │         Row Data            │ │ │  │
│  │  │  │ Metadata    │    │                             │ │ │  │
│  │  │  │ - Columns   │    │  {                          │ │ │  │
│  │  │  │ - Types     │    │    "1": {"id": 1, ...},     │ │ │  │
│  │  │  │ - Constraints│   │    "2": {"id": 2, ...}     │ │ │  │
│  │  │  └─────────────┘    │  }                          │ │ │  │
│  │  │                     └─────────────────────────────┘ │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
SQL Query → Tokenizer → Parser → AST → Executor → Engine → Storage
    ↑                                      ↓         ↓        ↓
    └── Results ← Formatter ← Result Set ←─┘    Index  JSON File
                                              Lookup
```

### Core Components

### Query Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Query Execution Flow                         │
└─────────────────────────────────────────────────────────────────┘

1. SQL Input
   │
   ▼
┌─────────────┐    "SELECT * FROM users WHERE id = 1"
│ Tokenizer   │ ──────────────────────────────────────┐
└─────────────┘                                       │
   │                                                  ▼
   ▼                                            [SELECT, *, FROM, 
┌─────────────┐                                 users, WHERE, id, 
│   Parser    │                                 =, 1]
└─────────────┘                                       │
   │                                                  │
   ▼                                                  │
┌─────────────┐    SelectStmt {                       │
│ AST Builder │      columns: ['*'],          ◄──────┘
└─────────────┘      table: 'users',
   │                 where: {column: 'id', op: '=', value: 1}
   ▼               }
┌─────────────┐
│  Executor   │ ──┐
└─────────────┘   │
   │              │ Index Available?
   ▼              │
┌─────────────┐   │  YES: Use B-Tree lookup O(log n)
│   Engine    │ ◄─┤  
└─────────────┘   │  NO:  Full table scan O(n)
   │              │
   ▼              │
┌─────────────┐   │
│   Result    │ ◄─┘
│  Formatter  │
└─────────────┘
   │
   ▼
┌─────────────┐
│   Output    │    id | name  | email
└─────────────┘    ---|-------|-------
                    1 | Alice | alice@test.com
```

### B-Tree Index Structure

```
                    Root Node
                   ┌─────────┐
                   │   [5]   │
                   └────┬────┘
                        │
           ┌────────────┴────────────┐
           ▼                         ▼
    ┌─────────────┐           ┌─────────────┐
    │   [2, 3]    │           │  [7, 9]     │
    └──┬────┬─────┘           └──┬────┬─────┘
       │    │                    │    │
       ▼    ▼                    ▼    ▼
    ┌────┐┌────┐              ┌────┐┌────┐
    │{1} ││{2,3}│             │{6,7}││{8,9}│  ← Leaf nodes contain
    │{4} ││{5} │              │{10}││{11}│    sets of row IDs
    └────┘└────┘              └────┘└────┘
```
### Component Details

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

## What Makes MiniDB Special

### Built from Scratch
- Zero external database libraries: Every component implemented from first principles
- Custom SQL parser: Hand-written tokenizer and recursive descent parser
- Native B-Tree implementation: Self-balancing tree with O(log n) operations
- Query execution engine: Complete pipeline from parsing to result formatting

### Production-Quality Code
- Modular architecture: Clean separation of concerns across components
- Comprehensive error handling: Meaningful error messages and validation
- Extensive documentation: Both code comments and architectural explanations
- Real-world demo: Working web application showing practical usage

### Educational Value
- Demonstrates core CS concepts: Data structures, algorithms, language design
- Shows system design thinking: Layered architecture and component interaction
- Illustrates trade-offs: Performance vs. simplicity, features vs. complexity
- Provides learning resource: Clear code that others can study and extend

## Current Limitations

MiniDB is a demonstration project with several intentional limitations that would need to be addressed for production use:

### Concurrency & Transactions
- Single-threaded: No concurrent access support
- No ACID guarantees: No transaction isolation or atomicity
- No locking: Race conditions possible with multiple writers
- No WAL: No write-ahead logging for crash recovery

### SQL Feature Set
- Limited JOIN types: Only INNER JOIN implemented
- No subqueries: Nested SELECT statements not supported
- No aggregations: No GROUP BY, COUNT, SUM, AVG functions
- No advanced clauses: No HAVING, UNION, or window functions
- Basic data types: Only INTEGER, TEXT, FLOAT, BOOLEAN

### Performance & Scalability
- Memory-only: Entire database loaded into RAM
- No query optimization: Simple nested-loop joins only
- No statistics: No cost-based query planning
- Single-file storage: No partitioning or sharding

### Storage Engine
- JSON format: Human-readable but inefficient for large datasets
- No compression: Storage not optimized for space
- No backup/restore: No built-in backup mechanisms
- No replication: Single point of failure

### Security & Administration
- No authentication: No user management or access control
- No encryption: Data stored in plain text
- No audit logging: No tracking of database operations
- No configuration: Limited tuning options

These limitations were conscious design choices to keep the implementation focused on core database concepts while maintaining code clarity and demonstrating fundamental understanding of RDBMS internals.

## Testing & Verification

### Quick Verification Test

Run this comprehensive test to verify all major features work:

```bash
python -c "
from minidb.engine import Database
from minidb.executor import Executor

print('Testing MiniDB Core Features...\n')

db = Database()
ex = Executor(db)

# Test 1: Table Creation
print('Creating table with constraints...')
ex.execute('CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price FLOAT, category TEXT UNIQUE)')

# Test 2: Data Insertion
print('Inserting test data...')
ex.execute(\"INSERT INTO products VALUES (1, 'Laptop', 999.99, 'Electronics')\")
ex.execute(\"INSERT INTO products VALUES (2, 'Book', 19.99, 'Education')\")

# Test 3: Queries
print('Testing SELECT queries...')
result = ex.execute('SELECT * FROM products WHERE price > 50')
assert len(result.rows) == 1

# Test 4: Updates
print('Testing UPDATE operations...')
ex.execute('UPDATE products SET price = 899.99 WHERE id = 1')

# Test 5: Joins
print('Testing JOIN operations...')
ex.execute('CREATE TABLE reviews (id INTEGER PRIMARY KEY, product_id INTEGER, rating INTEGER)')
ex.execute('INSERT INTO reviews VALUES (1, 1, 5)')
result = ex.execute('SELECT products.name, reviews.rating FROM products JOIN reviews ON products.id = reviews.product_id')
assert len(result.rows) == 1

# Test 6: Constraints
print('Testing constraint validation...')
try:
    ex.execute(\"INSERT INTO products VALUES (3, 'Tablet', 299.99, 'Electronics')\")
    print('ERROR: Unique constraint should have failed!')
except ValueError:
    print('Unique constraint properly enforced')

print('\nAll tests passed! MiniDB is working correctly.')
"
```

### Manual Testing with REPL

For interactive testing, use the REPL commands:

```bash
python -m minidb.repl

# Try these commands:
.help          # Show available commands
.tables        # List all tables
.schema users  # Show table structure
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

## Project Reflection

### Technical Achievements
This project demonstrates practical implementation of fundamental computer science concepts:

- Data Structures: B-Trees for efficient indexing and search operations
- Language Design: Complete SQL parser with tokenization and AST generation  
- Systems Programming: Storage engine with persistence and crash safety
- Algorithm Design: Query optimization and execution planning
- Software Architecture: Modular design with clear component boundaries

### Design Philosophy
MiniDB prioritizes clarity over performance and education over features. Every design decision favors code readability and conceptual understanding while still delivering a genuinely functional system.

### Future Enhancements
The modular architecture makes MiniDB easily extensible. Priority improvements would include:

1. Concurrency control with row-level locking
2. Transaction support with ACID guarantees
3. Query optimization with cost-based planning
4. Additional SQL features (GROUP BY, subqueries, etc.)
5. Network protocol for client-server architecture

## Credits

Built from scratch as a coding challenge submission. No external database libraries used.

The implementation demonstrates understanding of:
- Database storage engines and indexing strategies
- SQL parsing techniques and query execution
- System design principles and software architecture
- Performance considerations and optimization trade-offs

Repository: https://github.com/Copubah/minidb

## License

This project is provided as-is for educational and demonstration purposes.
