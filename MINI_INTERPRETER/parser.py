"""
Parser: Converts a flat token list into an Abstract Syntax Tree (AST).

Grammar:
  program    := statement*
  statement  := assign | print_stmt | expr
  assign     := IDENTIFIER '=' expr
  print_stmt := 'print' expr
  expr       := comparison
  comparison := addition (('>' | '<' | '==' | '!=' | '<=' | '>=') addition)*
  addition   := term (('+' | '-') term)*
  term       := unary (('*' | '/') unary)*
  unary      := '-' unary | primary
  primary    := NUMBER | IDENTIFIER | '(' expr ')' | if_expr
  if_expr    := 'if' expr ':' expr 'else' expr
"""


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ── Helpers ──────────────────────────────────────────────────────────────

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', 'EOF')

    def peek_type(self):
        return self.peek()[0]

    def peek_value(self):
        return self.peek()[1]

    def consume(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, tok_type, value=None):
        tok = self.consume()
        if tok[0] != tok_type:
            raise SyntaxError(
                f"Expected token type '{tok_type}', got '{tok[0]}' ('{tok[1]}')"
            )
        if value is not None and tok[1] != value:
            raise SyntaxError(
                f"Expected '{value}', got '{tok[1]}'"
            )
        return tok

    # ── Grammar rules ─────────────────────────────────────────────────────────

    def parse_program(self):
        stmts = []
        while self.peek_type() != 'EOF':
            stmts.append(self.parse_statement())
        if len(stmts) == 1:
            return stmts[0]
        return ('program', stmts)

    def parse_statement(self):
        # Assignment: IDENTIFIER '=' expr  (look-ahead)
        if (self.peek_type() == 'IDENTIFIER'
                and self.pos + 1 < len(self.tokens)
                and self.tokens[self.pos + 1] == ('OPERATOR', '=')):
            name = self.consume()[1]
            self.consume()            # consume '='
            value = self.parse_expr()
            return ('assign', name, value)

        # Print statement — tokenizer emits ('PRINT', 'print')
        if self.peek_type() == 'PRINT':
            self.consume()
            return ('print', self.parse_expr())

        return self.parse_expr()

    def parse_expr(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addition()
        CMP = {'>', '<', '==', '!=', '<=', '>='}
        while self.peek_type() == 'OPERATOR' and self.peek_value() in CMP:
            op = self.consume()[1]
            right = self.parse_addition()
            left = (op, left, right)
        return left

    def parse_addition(self):
        left = self.parse_term()
        while self.peek_type() == 'OPERATOR' and self.peek_value() in ('+', '-'):
            op = self.consume()[1]
            right = self.parse_term()
            left = (op, left, right)
        return left

    def parse_term(self):
        left = self.parse_unary()
        while self.peek_type() == 'OPERATOR' and self.peek_value() in ('*', '/'):
            op = self.consume()[1]
            right = self.parse_unary()
            left = (op, left, right)
        return left

    def parse_unary(self):
        if self.peek_type() == 'OPERATOR' and self.peek_value() == '-':
            self.consume()
            return ('negate', self.parse_unary())
        return self.parse_primary()

    def parse_primary(self):
        tok_type, tok_val = self.peek()

        # Number
        if tok_type == 'NUMBER':
            self.consume()
            return ('NUMBER', tok_val)

        # Identifier
        if tok_type == 'IDENTIFIER':
            self.consume()
            return ('IDENTIFIER', tok_val)

        # Grouped expression — tokenizer emits LPAREN / RPAREN
        if tok_type == 'LPAREN':
            self.consume()
            node = self.parse_expr()
            if self.peek_type() == 'RPAREN':
                self.consume()
            else:
                raise SyntaxError("Expected closing ')'")
            return node

        # If-else expression — tokenizer emits ('IF', 'if')
        if tok_type == 'IF':
            return self.parse_if()

        raise SyntaxError(
            f"Unexpected token: type='{tok_type}' value='{tok_val}'"
        )

    def parse_if(self):
        self.expect('IF', 'if')
        condition = self.parse_expr()
        # tokenizer emits ('COLON', ':')
        if self.peek_type() == 'COLON':
            self.consume()
        else:
            raise SyntaxError("Expected ':' after if-condition")
        true_branch = self.parse_expr()
        # tokenizer emits ('ELSE', 'else')
        if self.peek_type() == 'ELSE':
            self.consume()
        else:
            raise SyntaxError("Expected 'else'")
        false_branch = self.parse_expr()
        return ('if', condition, true_branch, false_branch)


# ── Public API ───────────────────────────────────────────────────────────────

def parse(tokens):
    """Parse a token list and return an AST."""
    p = Parser(tokens)
    return p.parse_program()