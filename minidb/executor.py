"""Query execution engine."""

from typing import Any, Dict, List, Optional
from .engine import Database, Column, Table
from .parser import (
    parse_sql, CreateTableStmt, DropTableStmt, InsertStmt,
    SelectStmt, UpdateStmt, DeleteStmt
)

class QueryResult:
    def __init__(self, columns: List[str] = None, rows: List[Dict] = None,
                 message: str = None, affected: int = 0):
        self.columns = columns or []
        self.rows = rows or []
        self.message = message
        self.affected = affected
    
    def __repr__(self):
        if self.message:
            return self.message
        if not self.rows:
            return "Empty result set"
        
        # Format as table
        col_widths = {col: len(col) for col in self.columns}
        for row in self.rows:
            for col in self.columns:
                val = str(row.get(col, 'NULL'))
                col_widths[col] = max(col_widths[col], len(val))
        
        lines = []
        header = ' | '.join(col.ljust(col_widths[col]) for col in self.columns)
        lines.append(header)
        lines.append('-' * len(header))
        
        for row in self.rows:
            line = ' | '.join(
                str(row.get(col, 'NULL')).ljust(col_widths[col])
                for col in self.columns
            )
            lines.append(line)
        
        lines.append(f"\n({len(self.rows)} rows)")
        return '\n'.join(lines)

class Executor:
    def __init__(self, db: Database):
        self.db = db
    
    def execute(self, sql: str) -> QueryResult:
        """Execute SQL and return result."""
        stmt = parse_sql(sql)
        
        if isinstance(stmt, CreateTableStmt):
            return self.exec_create(stmt)
        elif isinstance(stmt, DropTableStmt):
            return self.exec_drop(stmt)
        elif isinstance(stmt, InsertStmt):
            return self.exec_insert(stmt)
        elif isinstance(stmt, SelectStmt):
            return self.exec_select(stmt)
        elif isinstance(stmt, UpdateStmt):
            return self.exec_update(stmt)
        elif isinstance(stmt, DeleteStmt):
            return self.exec_delete(stmt)
        
        raise ValueError(f"Unknown statement type: {type(stmt)}")

    def exec_create(self, stmt: CreateTableStmt) -> QueryResult:
        columns = [
            Column(
                c['name'], c['type'], c['primary_key'],
                c['unique'], c['not_null']
            )
            for c in stmt.columns
        ]
        self.db.create_table(stmt.table_name, columns)
        return QueryResult(message=f"Table '{stmt.table_name}' created")
    
    def exec_drop(self, stmt: DropTableStmt) -> QueryResult:
        self.db.drop_table(stmt.table_name)
        return QueryResult(message=f"Table '{stmt.table_name}' dropped")
    
    def exec_insert(self, stmt: InsertStmt) -> QueryResult:
        table = self.db.get_table(stmt.table_name)
        
        if stmt.columns:
            values = dict(zip(stmt.columns, stmt.values))
        else:
            values = dict(zip(table.column_order, stmt.values))
        
        table.insert(values)
        self.db.save()
        return QueryResult(message="1 row inserted", affected=1)
    
    def exec_select(self, stmt: SelectStmt) -> QueryResult:
        table = self.db.get_table(stmt.table_name)
        
        # Get base rows
        if stmt.where and not stmt.joins:
            row_ids = self.filter_rows(table, stmt.where)
        else:
            row_ids = set(table.rows.keys())
        
        # Handle JOINs
        if stmt.joins:
            results = self.execute_joins(table, stmt.joins, row_ids, stmt.where)
        else:
            results = [table.rows[rid] for rid in row_ids]
        
        # Determine columns
        if stmt.columns == ['*']:
            if stmt.joins:
                columns = list(results[0].keys()) if results else []
            else:
                columns = table.column_order
        else:
            columns = stmt.columns
        
        # Order results
        if stmt.order_by:
            for col, direction in reversed(stmt.order_by):
                reverse = direction == 'DESC'
                results.sort(key=lambda r: (r.get(col) is None, r.get(col)), reverse=reverse)
        
        # Apply limit
        if stmt.limit:
            results = results[:stmt.limit]
        
        return QueryResult(columns=columns, rows=results)

    def exec_update(self, stmt: UpdateStmt) -> QueryResult:
        table = self.db.get_table(stmt.table_name)
        
        if stmt.where:
            row_ids = self.filter_rows(table, stmt.where)
        else:
            row_ids = set(table.rows.keys())
        
        for rid in row_ids:
            table.update(rid, stmt.assignments)
        
        self.db.save()
        return QueryResult(message=f"{len(row_ids)} row(s) updated", affected=len(row_ids))
    
    def exec_delete(self, stmt: DeleteStmt) -> QueryResult:
        table = self.db.get_table(stmt.table_name)
        
        if stmt.where:
            row_ids = self.filter_rows(table, stmt.where)
        else:
            row_ids = set(table.rows.keys())
        
        for rid in list(row_ids):
            table.delete(rid)
        
        self.db.save()
        return QueryResult(message=f"{len(row_ids)} row(s) deleted", affected=len(row_ids))
    
    def filter_rows(self, table: Table, condition: Dict) -> set:
        """Filter rows based on WHERE condition."""
        if 'column' in condition:
            return self.eval_comparison(table, condition)
        
        # AND/OR
        op = condition['op']
        left = self.filter_rows(table, condition['left'])
        right = self.filter_rows(table, condition['right'])
        
        if op == 'AND':
            return left & right
        else:  # OR
            return left | right
    
    def eval_comparison(self, table: Table, cond: Dict) -> set:
        """Evaluate a single comparison."""
        col = cond['column']
        op = cond['op']
        value = cond['value']
        
        # Try index lookup for equality
        if op == '=' and col in table.indexes:
            return table.get_row_ids_by_index(col, value) or set()
        
        # Full scan
        result = set()
        for rid, row in table.rows.items():
            row_val = row.get(col)
            if self.compare(row_val, op, value):
                result.add(rid)
        return result
    
    def compare(self, left: Any, op: str, right: Any) -> bool:
        """Compare two values."""
        if left is None or right is None:
            return False
        
        if op == '=':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right
        return False

    def execute_joins(self, base_table: Table, joins: List[Dict],
                      base_row_ids: set, where: Optional[Dict]) -> List[Dict]:
        """Execute JOIN operations."""
        results = []
        
        for rid in base_row_ids:
            row = base_table.rows[rid].copy()
            # Prefix columns with table name
            prefixed = {f"{base_table.name}.{k}": v for k, v in row.items()}
            prefixed.update(row)  # Also keep unprefixed
            results.append(prefixed)
        
        for join in joins:
            join_table = self.db.get_table(join['table'])
            new_results = []
            
            for result_row in results:
                left_col = join['left']
                right_col = join['right']
                
                # Get the value to match
                left_val = result_row.get(left_col)
                
                # Find matching rows in join table
                for jrid, jrow in join_table.rows.items():
                    # Determine which column to match
                    if '.' in right_col:
                        _, rcol = right_col.split('.', 1)
                    else:
                        rcol = right_col
                    
                    if jrow.get(rcol) == left_val:
                        merged = result_row.copy()
                        # Add join table columns
                        for k, v in jrow.items():
                            merged[f"{join['table']}.{k}"] = v
                            merged[k] = v
                        new_results.append(merged)
            
            results = new_results
        
        # Apply WHERE filter on joined results
        if where:
            results = [r for r in results if self.eval_condition_on_row(r, where)]
        
        return results
    
    def eval_condition_on_row(self, row: Dict, condition: Dict) -> bool:
        """Evaluate condition on a single row."""
        if 'column' in condition:
            col = condition['column']
            op = condition['op']
            value = condition['value']
            return self.compare(row.get(col), op, value)
        
        op = condition['op']
        left = self.eval_condition_on_row(row, condition['left'])
        right = self.eval_condition_on_row(row, condition['right'])
        
        if op == 'AND':
            return left and right
        return left or right
