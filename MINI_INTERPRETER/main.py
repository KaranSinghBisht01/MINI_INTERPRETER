"""
Main entry point for the Mini Interpreter (CLI mode).
"""

import tokenizer
import parser as parser_module
import ir_generator
import ir_executor


def interpret(code):
    """Run the full interpreter pipeline on source code."""
    print("\n" + "="*50)
    print(f"📝 Source Code:\n{code}")
    print("="*50) 

    
    tokens = tokenizer.tokenize(code)
    print(f"\n🔹 Tokens:\n{tokens}")

    
    ast = parser_module.parse(tokens)
    print(f"\n🔸 AST:\n{ast}")

    
    ir_code = ir_generator.generate_ir(ast)
    print(f"\n⚙️  IR Code:")
    for i, instr in enumerate(ir_code):
        print(f"   {i:02d}: {instr}")

    
    result = ir_executor.execute_ir(ir_code)
    print(f"\n✅ Output: {result['output']}")
    print(f"   Result: {result['result']}")
    print(f"   Variables: {result['variables']}")
    print("="*50 + "\n")

    return result


def main():
    print("╔══════════════════════════════════════╗")
    print("║      Mini Interpreter v2.0           ║")
    print("║   Compiler Design Project            ║")
    print("╚══════════════════════════════════════╝")
    print("\nSupported syntax:")
    print("  Arithmetic : 3 + 5 * 2")
    print("  Comparison : 10 > 5")
    print("  If-Else    : if 10 > 5 : 100 else 200")
    print("  Assignment : x = 42  (in GUI/multi-line)")
    print("  Print      : print 3 + 4")
    print("\nType 'exit' to quit.\n")

    while True:
        try:
            code = input(">>> ").strip()
            if code.lower() == 'exit':
                print("👋 Goodbye!")
                break
            if not code:
                continue
            interpret(code)
        except (SyntaxError, NameError,
                ZeroDivisionError, ValueError) as e:
            print(f"❌ Error: {e}")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


if __name__ == '__main__':
    main()