"""
IR Executor: Executes stack-based IR instructions.

Maintains:
 stack: operand stack
 variables: symbol table for variables
 output: collected print output
 ip: instruction pointer
"""


def execute_ir(ir_code):
    """
    Execute IR instructions and return result.

    Returns:
        dict with 'result' (final stack value) and 'output' (printed lines)
    """
    stack = []
    variables = {}
    output_lines = []
    ip = 0  

    while ip < len(ir_code):
        instr = ir_code[ip]

        
        if instr.startswith('PUSH'):
            _, val = instr.split()
            
            stack.append(float(val) if '.' in val else int(val))

     
        elif instr.startswith('LOAD'):
            _, name = instr.split()
            if name not in variables:
                raise NameError(f"Variable '{name}' is not defined")
            stack.append(variables[name])

      
        elif instr.startswith('STORE'):
            _, name = instr.split()
            variables[name] = stack.pop()

       
        elif instr == 'NEG':
            a = stack.pop()
            stack.append(-a)

      
        elif instr == 'ADD':
            b, a = stack.pop(), stack.pop()
            stack.append(a + b)

        elif instr == 'SUB':
            b, a = stack.pop(), stack.pop()
            stack.append(a - b)

        elif instr == 'MUL':
            b, a = stack.pop(), stack.pop()
            stack.append(a * b)

        elif instr == 'DIV':
            b, a = stack.pop(), stack.pop()
            if b == 0:
                raise ZeroDivisionError("Division by zero")
            stack.append(a / b)

        
        elif instr == 'GT':
            b, a = stack.pop(), stack.pop()
            stack.append(1 if a > b else 0)

        elif instr == 'LT':
            b, a = stack.pop(), stack.pop()
            stack.append(1 if a < b else 0)

        elif instr == 'EQ':
            b, a = stack.pop(), stack.pop()
            stack.append(1 if a == b else 0)

        elif instr == 'NEQ':
            b, a = stack.pop(), stack.pop()
            stack.append(1 if a != b else 0)

        elif instr == 'LEQ':
            b, a = stack.pop(), stack.pop()
            stack.append(1 if a <= b else 0)

        elif instr == 'GEQ':
            b, a = stack.pop(), stack.pop()
            stack.append(1 if a >= b else 0)

        # ── Control Flow ───────────────────────────────────────────────────
        elif instr.startswith('IF_FALSE'):
            _, target = instr.split()
            condition = stack.pop()
            if not condition:
                ip = int(target)
                continue  

        elif instr.startswith('JUMP'):
            _, target = instr.split()
            ip = int(target)
            continue  # skip ip += 1

        
        elif instr == 'PRINT':
            value = stack.pop()
            
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            output_lines.append(str(value))

        else:
            raise ValueError(f"Unknown IR instruction: {instr!r}")

        ip += 1

    
    final_result = stack[-1] if stack else None
    if isinstance(final_result, float) and final_result.is_integer():
        final_result = int(final_result)

    return {
        'result': final_result,
        'output': '\n'.join(output_lines),
        'variables': variables
    }