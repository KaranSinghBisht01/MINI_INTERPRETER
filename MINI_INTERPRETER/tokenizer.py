import re

def tokenize(code):
    """
    Tokenizer: Converts raw source code into a list of tokens.
    
    Supported tokens:
    - IF, ELSE: keywords
    - NUMBER: integers
    - IDENTIFIER: variable names
    - OPERATOR: +, -, *, /, >, <, ==, !=, <=, >=
    - ASSIGN: =
    - LPAREN, RPAREN: ( )
    - COLON: :
    - PRINT: print keyword
    """
    token_specification = [
        ('NUMBER',     r'\d+(\.\d*)?'),          # Integer or decimal number
        ('ASSIGN',     r'=='),                    # Equality check (before OPERATOR)
        ('NEQ',        r'!='),                    # Not equal
        ('LEQ',        r'<='),                    # Less or equal
        ('GEQ',        r'>='),                    # Greater or equal
        ('OPERATOR',   r'[+\-*/<>=]'),            # Arithmetic/comparison operators
        ('LPAREN',     r'\('),                    # Left parenthesis
        ('RPAREN',     r'\)'),                    # Right parenthesis
        ('COLON',      r':'),                     # Colon
        ('IF',         r'\bif\b'),                # if keyword
        ('ELSE',       r'\belse\b'),              # else keyword
        ('PRINT',      r'\bprint\b'),             # print keyword
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),# Variable names
        ('SKIP',       r'[ \t]+'),                # Whitespace (skip)
        ('NEWLINE',    r'\n'),                    # Newline
        ('MISMATCH',   r'.'),                     # Any other character
    ]

    tok_regex = '|'.join(
        f'(?P<{name}>{pattern})' for name, pattern in token_specification
    )

    tokens = []

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()

        if kind == 'NUMBER':
            # Convert to float or int
            value = float(value) if '.' in value else int(value)
            tokens.append(('NUMBER', value))

        elif kind in ('ASSIGN', 'NEQ', 'LEQ', 'GEQ'):
            # Multi-character operators
            tokens.append(('OPERATOR', value))

        elif kind == 'OPERATOR':
            tokens.append(('OPERATOR', value))

        elif kind in ('IF', 'ELSE', 'PRINT',
                      'LPAREN', 'RPAREN', 'COLON', 'IDENTIFIER'):
            tokens.append((kind, value))

        elif kind == 'MISMATCH':
            raise SyntaxError(f"Unexpected character: {value!r}")

        # SKIP and NEWLINE are ignored

    return tokens