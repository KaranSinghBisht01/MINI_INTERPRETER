"""
IR Generator: Converts AST into stack-based Intermediate Representation.

IR Instructions:
- PUSH <value>    : Push number onto stack
- LOAD <name>     : Load variable value onto stack
- STORE <name>    : Store top of stack into variable
- ADD             : Pop two values, push sum
- SUB             : Pop two values, push difference
- MUL             : Pop two values, push product
- DIV             : Pop two values, push quotient
- GT              : Pop two values, push 1 if a > b else 0
- LT              : Pop two values, push 1 if a < b else 0
- EQ              : Pop two values, push 1 if a == b else 0
- NEQ             : Pop two values, push 1 if a != b else 0
- LEQ             : Pop two values, push 1 if a <= b else 0
- GEQ             : Pop two values, push 1 if a >= b else 0
- NEG             : Negate top of stack
- IF_FALSE <n>    : Pop condition, jump n steps if false
- JUMP <n>        : Unconditional jump n steps
- PRINT           : Pop and print top of stack
"""

OPERATOR_MAP = {
    '+':  'ADD',
    '-':  'SUB',
    '*':  'MUL',
    '/':  'DIV',
    '>':  'GT',
    '<':  'LT',
    '==': 'EQ',
    '!=': 'NEQ',
    '<=': 'LEQ',
    '>=': 'GEQ',
}


def generate_ir(ast):
    """Main IR generation entry point."""
    ir = []
    _generate(ast, ir)
    return ir


def _generate(node, ir):
    """Recursively generate IR instructions from AST node."""

    if node is None:
        return

    node_type = node[0]

    # ── Program (multiple statements) ──────────────────────────────────────
    if node_type == 'program':
        for stmt in node[1]:
            _generate(stmt, ir)

    # ── Number literal ──────────────────────────────────────────────────────
    elif node_type == 'NUMBER':
        ir.append(f'PUSH {node[1]}')

    # ── Variable reference ──────────────────────────────────────────────────
    elif node_type == 'IDENTIFIER':
        ir.append(f'LOAD {node[1]}')

    # ── Assignment ──────────────────────────────────────────────────────────
    elif node_type == 'assign':
        _, name, value_node = node
        _generate(value_node, ir)
        ir.append(f'STORE {name}')

    # ── Unary negation ──────────────────────────────────────────────────────
    elif node_type == 'negate':
        _generate(node[1], ir)
        ir.append('NEG')

    # ── Binary operators ────────────────────────────────────────────────────
    elif node_type in OPERATOR_MAP:
        _generate(node[1], ir)   # left operand
        _generate(node[2], ir)   # right operand
        ir.append(OPERATOR_MAP[node_type])

    # ── If-else ─────────────────────────────────────────────────────────────
    elif node_type == 'if':
        _, condition, true_branch, false_branch = node

        # Generate condition
        _generate(condition, ir)

        # Placeholder for IF_FALSE jump
        if_false_idx = len(ir)
        ir.append('IF_FALSE ?')

        # True branch
        _generate(true_branch, ir)

        # Placeholder for JUMP (skip false branch)
        jump_idx = len(ir)
        ir.append('JUMP ?')

        # Patch IF_FALSE to jump here (start of false branch)
        false_start = len(ir)
        ir[if_false_idx] = f'IF_FALSE {false_start}'

        # False branch
        _generate(false_branch, ir)

        # Patch JUMP to jump here (end of if-else)
        end_idx = len(ir)
        ir[jump_idx] = f'JUMP {end_idx}'

    # ── Print ───────────────────────────────────────────────────────────────
    elif node_type == 'print':
        _generate(node[1], ir)
        ir.append('PRINT')

    else:
        raise ValueError(f"Unknown AST node type: {node_type}")