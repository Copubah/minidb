"""Core database engine with storage and indexing."""

import json
import os
from typing import Any, Dict, List, Optional, Set
from .btree import BTree

class Column:
    def __init__(self, name: str, dtype: str, primary_key: bool = False,
                 unique: bool = False, not_null: bool = False):
        self.name = name
        self.dtype = dtype.upper()
        self.primary_key = primary_key
        self.unique = unique or primary_key
        self.not_null = not_null or primary_key

class Table:
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.column_order = [col.name for col in columns]
        self.rows: Dict[int, Dict[str, Any]] = {}
        self.next_row_id = 1
        self.indexes: Dict[str, BTree] = {}
        
        # Create indexes for primary key and unique columns
        for col in columns:
            if col.primary_key or col.unique:
                self.indexes[col.name] = BTree()
    
    def validate_value(self, col_name: str, value: Any) -> Any:
        """Validate and convert value to correct type."""
        col = self.columns[col_name]
        
        if value is None:
            if col.not_null:
                raise ValueError(f"Column '{col_name}' cannot be NULL")
            return None
        
        try:
            if col.dtype == 'INTEGER':
                return int(value)
            elif col.dtype == 'FLOAT':
                return float(value)
            elif col.dtype == 'TEXT':
                return str(value)
            elif col.dtype == 'BOOLEAN':
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes')
                return bool(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid value '{value}' for {col.dtype} column '{col_name}'")
        return value

    def insert(self, values: Dict[str, Any]) -> int:
        """Insert a row and return its row_id."""
        row = {}
        for col_name in self.column_order:
            col = self.columns[col_name]
            value = values.get(col_name)
            validated = self.validate_value(col_name, value)
            
            # Check unique constraint
            if col.unique and validated is not None:
                if col_name in self.indexes:
                    existing = self.indexes[col_name].search(validated)
                    if existing:
                        raise ValueError(f"Duplicate value '{validated}' for unique column '{col_name}'")
            row[col_name] = validated
        
        row_id = self.next_row_id
        self.next_row_id += 1
        self.rows[row_id] = row
        
        # Update indexes
        for col_name, index in self.indexes.items():
            if row[col_name] is not None:
                index.insert(row[col_name], row_id)
        
        return row_id
    
    def update(self, row_id: int, values: Dict[str, Any]):
        """Update a row by row_id."""
        if row_id not in self.rows:
            raise ValueError(f"Row {row_id} not found")
        
        old_row = self.rows[row_id]
        new_row = old_row.copy()
        
        for col_name, value in values.items():
            if col_name not in self.columns:
                raise ValueError(f"Unknown column '{col_name}'")
            col = self.columns[col_name]
            validated = self.validate_value(col_name, value)
            
            # Check unique constraint
            if col.unique and validated is not None and validated != old_row.get(col_name):
                if col_name in self.indexes:
                    existing = self.indexes[col_name].search(validated)
                    if existing:
                        raise ValueError(f"Duplicate value '{validated}' for unique column '{col_name}'")
            new_row[col_name] = validated
        
        # Update indexes
        for col_name, index in self.indexes.items():
            old_val = old_row.get(col_name)
            new_val = new_row.get(col_name)
            if old_val != new_val:
                if old_val is not None:
                    index.delete(old_val, row_id)
                if new_val is not None:
                    index.insert(new_val, row_id)
        
        self.rows[row_id] = new_row
    
    def delete(self, row_id: int):
        """Delete a row by row_id."""
        if row_id not in self.rows:
            return
        row = self.rows[row_id]
        
        # Update indexes
        for col_name, index in self.indexes.items():
            if row.get(col_name) is not None:
                index.delete(row[col_name], row_id)
        
        del self.rows[row_id]
    
    def get_row_ids_by_index(self, col_name: str, value: Any) -> Set[int]:
        """Get row IDs using index lookup."""
        if col_name in self.indexes:
            return self.indexes[col_name].search(value)
        return None  # No index available


class Database:
    def __init__(self, path: str = None):
        self.tables: Dict[str, Table] = {}
        self.path = path
        if path and os.path.exists(path):
            self.load()
    
    def create_table(self, name: str, columns: List[Column]):
        """Create a new table."""
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        self.tables[name] = Table(name, columns)
        self.save()
    
    def drop_table(self, name: str):
        """Drop a table."""
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist")
        del self.tables[name]
        self.save()
    
    def get_table(self, name: str) -> Table:
        """Get a table by name."""
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist")
        return self.tables[name]
    
    def save(self):
        """Persist database to disk."""
        if not self.path:
            return
        
        data = {}
        for table_name, table in self.tables.items():
            data[table_name] = {
                'columns': [
                    {
                        'name': col.name,
                        'dtype': col.dtype,
                        'primary_key': col.primary_key,
                        'unique': col.unique,
                        'not_null': col.not_null
                    }
                    for col in [table.columns[n] for n in table.column_order]
                ],
                'rows': {str(k): v for k, v in table.rows.items()},
                'next_row_id': table.next_row_id
            }
        
        os.makedirs(os.path.dirname(self.path) or '.', exist_ok=True)
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load database from disk."""
        if not self.path or not os.path.exists(self.path):
            return
        
        with open(self.path, 'r') as f:
            data = json.load(f)
        
        for table_name, table_data in data.items():
            columns = [
                Column(
                    c['name'], c['dtype'], c['primary_key'],
                    c['unique'], c['not_null']
                )
                for c in table_data['columns']
            ]
            table = Table(table_name, columns)
            table.next_row_id = table_data['next_row_id']
            
            for row_id_str, row in table_data['rows'].items():
                row_id = int(row_id_str)
                table.rows[row_id] = row
                for col_name, index in table.indexes.items():
                    if row.get(col_name) is not None:
                        index.insert(row[col_name], row_id)
            
            self.tables[table_name] = table
