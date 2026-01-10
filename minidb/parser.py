"""SQL tokenizer and parser."""

import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

# Token types
KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET',
    'DELETE', 'CREATE', 'TABLE', 'DROP', 'AND', 'OR', 'NOT', 'NULL', 'PRIMARY',
    'KEY', 'UNIQUE', 'INTEGER', 'TEXT', 'FLOAT', 'BOOLEAN', 'JOIN', 'INNER',
    'ON', 'AS', 'ORDER', 'BY', 'ASC', 'DESC', 'LIMIT'
}

@dataclass
class Token:
    type: str
    value: Any

class Tokenizer:
    def __init__(self, sql: str):
        self.sql = sql
        self.pos = 0
        self.tokens = []
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.sql):
            self.skip_whitespace()
            if self.pos >= len(self.sql):
                break
            
            char = self.sql[self.pos]
            
            if char in '(),;*=<>!.':
                self.tokens.append(self.read_operator())
            elif char in ('"', "'"):
                self.tokens.append(self.read_string())
            elif char.isdigit() or (char == '-' and self.peek_digit()):
                self.tokens.append(self.read_number())
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
            else:
                self.pos += 1
        
        return self.tokens
    
    def skip_whitespace(self):
        while self.pos < len(self.sql) and self.sql[self.pos].isspace():
            self.pos += 1
    
    def peek_digit(self) -> bool:
        return self.pos + 1 < len(self.sql) and self.sql[self.pos + 1].isdigit()
    
    def read_operator(self) -> Token:
        char = self.sql[self.pos]
        self.pos += 1
        
        # Handle two-char operators
        if self.pos < len(self.sql):
            two_char = char + self.sql[self.pos]
            if two_char in ('<=', '>=', '!=', '<>'):
                self.pos += 1
                return Token('OP', two_char)
        
        return Token('OP', char)
    
    def read_string(self) -> Token:
        quote = self.sql[self.pos]
        self.pos += 1
        start = self.pos
        while self.pos < len(self.sql) and self.sql[self.pos] != quote:
            self.pos += 1
        value = self.sql[start:self.pos]
        self.pos += 1  # Skip closing quote
        return Token('STRING', value)
    
    def read_number(self) -> Token:
        start = self.pos
        if self.sql[self.pos] == '-':
            self.pos += 1
        while self.pos < len(self.sql) and (self.sql[self.pos].isdigit() or self.sql[self.pos] == '.'):
            self.pos += 1
        value = self.sql[start:self.pos]
        return Token('NUMBER', float(value) if '.' in value else int(value))
    
    def read_identifier(self) -> Token:
        start = self.pos
        while self.pos < len(self.sql) and (self.sql[self.pos].isalnum() or self.sql[self.pos] == '_'):
            self.pos += 1
        value = self.sql[start:self.pos]
        if value.upper() in KEYWORDS:
            return Token('KEYWORD', value.upper())
        return Token('IDENT', value)


@dataclass
class CreateTableStmt:
    table_name: str
    columns: List[Dict]

@dataclass
class DropTableStmt:
    table_name: str

@dataclass
class InsertStmt:
    table_name: str
    columns: List[str]
    values: List[Any]

@dataclass
class SelectStmt:
    columns: List[str]
    table_name: str
    joins: List[Dict]
    where: Optional[Any]
    order_by: Optional[List[Tuple[str, str]]]
    limit: Optional[int]

@dataclass
class UpdateStmt:
    table_name: str
    assignments: Dict[str, Any]
    where: Optional[Any]

@dataclass
class DeleteStmt:
    table_name: str
    where: Optional[Any]

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else None
    
    def consume(self, expected_type: str = None, expected_value: Any = None) -> Token:
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.type}")
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected '{expected_value}', got '{token.value}'")
        self.pos += 1
        return token
    
    def match(self, type_: str, value: Any = None) -> bool:
        token = self.current()
        if token and token.type == type_:
            if value is None or token.value == value:
                return True
        return False
    
    def parse(self):
        token = self.current()
        if not token:
            raise SyntaxError("Empty query")
        
        if token.type == 'KEYWORD':
            if token.value == 'CREATE':
                return self.parse_create()
            elif token.value == 'DROP':
                return self.parse_drop()
            elif token.value == 'INSERT':
                return self.parse_insert()
            elif token.value == 'SELECT':
                return self.parse_select()
            elif token.value == 'UPDATE':
                return self.parse_update()
            elif token.value == 'DELETE':
                return self.parse_delete()
        
        raise SyntaxError(f"Unknown statement: {token.value}")

    def parse_create(self) -> CreateTableStmt:
        self.consume('KEYWORD', 'CREATE')
        self.consume('KEYWORD', 'TABLE')
        table_name = self.consume('IDENT').value
        self.consume('OP', '(')
        
        columns = []
        while True:
            col_name = self.consume('IDENT').value
            col_type = self.consume('KEYWORD').value
            
            col_def = {'name': col_name, 'type': col_type, 'primary_key': False,
                       'unique': False, 'not_null': False}
            
            # Parse constraints
            while self.match('KEYWORD'):
                kw = self.current().value
                if kw == 'PRIMARY':
                    self.consume()
                    self.consume('KEYWORD', 'KEY')
                    col_def['primary_key'] = True
                elif kw == 'UNIQUE':
                    self.consume()
                    col_def['unique'] = True
                elif kw == 'NOT':
                    self.consume()
                    self.consume('KEYWORD', 'NULL')
                    col_def['not_null'] = True
                else:
                    break
            
            columns.append(col_def)
            
            if self.match('OP', ','):
                self.consume()
            else:
                break
        
        self.consume('OP', ')')
        return CreateTableStmt(table_name, columns)
    
    def parse_drop(self) -> DropTableStmt:
        self.consume('KEYWORD', 'DROP')
        self.consume('KEYWORD', 'TABLE')
        table_name = self.consume('IDENT').value
        return DropTableStmt(table_name)
    
    def parse_insert(self) -> InsertStmt:
        self.consume('KEYWORD', 'INSERT')
        self.consume('KEYWORD', 'INTO')
        table_name = self.consume('IDENT').value
        
        columns = []
        if self.match('OP', '('):
            self.consume()
            while True:
                columns.append(self.consume('IDENT').value)
                if self.match('OP', ','):
                    self.consume()
                else:
                    break
            self.consume('OP', ')')
        
        self.consume('KEYWORD', 'VALUES')
        self.consume('OP', '(')
        
        values = []
        while True:
            values.append(self.parse_value())
            if self.match('OP', ','):
                self.consume()
            else:
                break
        
        self.consume('OP', ')')
        return InsertStmt(table_name, columns, values)
    
    def parse_value(self) -> Any:
        token = self.current()
        if token.type == 'STRING':
            self.consume()
            return token.value
        elif token.type == 'NUMBER':
            self.consume()
            return token.value
        elif token.type == 'KEYWORD' and token.value == 'NULL':
            self.consume()
            return None
        elif token.type == 'IDENT':
            self.consume()
            val = token.value.lower()
            if val == 'true':
                return True
            elif val == 'false':
                return False
            return token.value
        raise SyntaxError(f"Expected value, got {token}")

    def parse_select(self) -> SelectStmt:
        self.consume('KEYWORD', 'SELECT')
        
        columns = []
        if self.match('OP', '*'):
            self.consume()
            columns = ['*']
        else:
            while True:
                col = self.consume('IDENT').value
                # Handle table.column notation
                if self.match('OP', '.'):
                    self.consume()
                    col = col + '.' + self.consume('IDENT').value
                columns.append(col)
                if self.match('OP', ','):
                    self.consume()
                elif self.match('KEYWORD', 'FROM'):
                    break
                else:
                    break
        
        self.consume('KEYWORD', 'FROM')
        table_name = self.consume('IDENT').value
        
        # Handle table alias
        table_alias = None
        if self.match('IDENT') or self.match('KEYWORD', 'AS'):
            if self.match('KEYWORD', 'AS'):
                self.consume()
            table_alias = self.consume('IDENT').value
        
        # Parse JOINs
        joins = []
        while self.match('KEYWORD', 'JOIN') or self.match('KEYWORD', 'INNER'):
            if self.match('KEYWORD', 'INNER'):
                self.consume()
            self.consume('KEYWORD', 'JOIN')
            join_table = self.consume('IDENT').value
            join_alias = None
            if self.match('IDENT') or self.match('KEYWORD', 'AS'):
                if self.match('KEYWORD', 'AS'):
                    self.consume()
                join_alias = self.consume('IDENT').value
            
            self.consume('KEYWORD', 'ON')
            left_col = self.consume('IDENT').value
            if self.match('OP', '.'):
                self.consume()
                left_col = left_col + '.' + self.consume('IDENT').value
            self.consume('OP', '=')
            right_col = self.consume('IDENT').value
            if self.match('OP', '.'):
                self.consume()
                right_col = right_col + '.' + self.consume('IDENT').value
            
            joins.append({
                'table': join_table,
                'alias': join_alias,
                'left': left_col,
                'right': right_col
            })
        
        # Parse WHERE
        where = None
        if self.match('KEYWORD', 'WHERE'):
            self.consume()
            where = self.parse_condition()
        
        # Parse ORDER BY
        order_by = None
        if self.match('KEYWORD', 'ORDER'):
            self.consume()
            self.consume('KEYWORD', 'BY')
            order_by = []
            while True:
                col = self.consume('IDENT').value
                direction = 'ASC'
                if self.match('KEYWORD', 'ASC'):
                    self.consume()
                elif self.match('KEYWORD', 'DESC'):
                    self.consume()
                    direction = 'DESC'
                order_by.append((col, direction))
                if self.match('OP', ','):
                    self.consume()
                else:
                    break
        
        # Parse LIMIT
        limit = None
        if self.match('KEYWORD', 'LIMIT'):
            self.consume()
            limit = int(self.consume('NUMBER').value)
        
        return SelectStmt(columns, table_name, joins, where, order_by, limit)

    def parse_update(self) -> UpdateStmt:
        self.consume('KEYWORD', 'UPDATE')
        table_name = self.consume('IDENT').value
        self.consume('KEYWORD', 'SET')
        
        assignments = {}
        while True:
            col = self.consume('IDENT').value
            self.consume('OP', '=')
            val = self.parse_value()
            assignments[col] = val
            if self.match('OP', ','):
                self.consume()
            else:
                break
        
        where = None
        if self.match('KEYWORD', 'WHERE'):
            self.consume()
            where = self.parse_condition()
        
        return UpdateStmt(table_name, assignments, where)
    
    def parse_delete(self) -> DeleteStmt:
        self.consume('KEYWORD', 'DELETE')
        self.consume('KEYWORD', 'FROM')
        table_name = self.consume('IDENT').value
        
        where = None
        if self.match('KEYWORD', 'WHERE'):
            self.consume()
            where = self.parse_condition()
        
        return DeleteStmt(table_name, where)
    
    def parse_condition(self):
        """Parse WHERE conditions with AND/OR support."""
        left = self.parse_comparison()
        
        while self.match('KEYWORD', 'AND') or self.match('KEYWORD', 'OR'):
            op = self.consume().value
            right = self.parse_comparison()
            left = {'op': op, 'left': left, 'right': right}
        
        return left
    
    def parse_comparison(self):
        """Parse a single comparison."""
        col = self.consume('IDENT').value
        # Handle table.column
        if self.match('OP', '.'):
            self.consume()
            col = col + '.' + self.consume('IDENT').value
        
        op = self.consume('OP').value
        if op == '<>':
            op = '!='
        
        value = self.parse_value()
        return {'column': col, 'op': op, 'value': value}


def parse_sql(sql: str):
    """Parse SQL string and return AST."""
    tokenizer = Tokenizer(sql)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
