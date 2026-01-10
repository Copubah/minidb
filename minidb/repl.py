"""Interactive REPL for MiniDB."""

import sys
import os
from .engine import Database
from .executor import Executor

def print_help():
    print("""
MiniDB - Simple RDBMS

Commands:
  .help          Show this help
  .tables        List all tables
  .schema TABLE  Show table schema
  .quit          Exit REPL

SQL Commands:
  CREATE TABLE name (col1 TYPE [constraints], ...)
  DROP TABLE name
  INSERT INTO name (cols) VALUES (vals)
  SELECT cols FROM table [WHERE cond] [ORDER BY col] [LIMIT n]
  UPDATE table SET col=val [WHERE cond]
  DELETE FROM table [WHERE cond]

Data Types: INTEGER, TEXT, FLOAT, BOOLEAN
Constraints: PRIMARY KEY, UNIQUE, NOT NULL

Example:
  CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
  INSERT INTO users (id, name) VALUES (1, 'Alice');
  SELECT * FROM users;
""")

def run_repl(db_path: str = 'minidb.json'):
    """Run interactive REPL."""
    db = Database(db_path)
    executor = Executor(db)
    
    print("MiniDB v1.0 - Type .help for help, .quit to exit")
    print(f"Database: {db_path}")
    print()
    
    while True:
        try:
            line = input("minidb> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        
        if not line:
            continue
        
        # Handle dot commands
        if line.startswith('.'):
            cmd = line.lower().split()
            if cmd[0] == '.quit' or cmd[0] == '.exit':
                print("Bye!")
                break
            elif cmd[0] == '.help':
                print_help()
            elif cmd[0] == '.tables':
                tables = list(db.tables.keys())
                if tables:
                    print('\n'.join(tables))
                else:
                    print("No tables")
            elif cmd[0] == '.schema' and len(cmd) > 1:
                table_name = cmd[1]
                if table_name in db.tables:
                    table = db.tables[table_name]
                    cols = []
                    for col_name in table.column_order:
                        col = table.columns[col_name]
                        parts = [col.name, col.dtype]
                        if col.primary_key:
                            parts.append('PRIMARY KEY')
                        elif col.unique:
                            parts.append('UNIQUE')
                        if col.not_null and not col.primary_key:
                            parts.append('NOT NULL')
                        cols.append(' '.join(parts))
                    print(f"CREATE TABLE {table_name} (")
                    print('  ' + ',\n  '.join(cols))
                    print(");")
                else:
                    print(f"Table '{table_name}' not found")
            else:
                print(f"Unknown command: {line}")
            continue
        
        # Execute SQL
        try:
            result = executor.execute(line)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
        print()

def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'minidb.json'
    run_repl(db_path)

if __name__ == '__main__':
    main()
