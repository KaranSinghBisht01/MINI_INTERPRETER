Mini Interpreter & VM
A stack-based interpreter built from scratch to demonstrate the full execution pipeline: from raw source code to a custom Intermediate Representation (IR), finally executing on a stack-oriented Virtual Machine.

🏗️ Architecture
The project is modularized into distinct phases:

Tokenizer (tokenizer.py): Converts raw source code into a stream of tokens, handling keywords, operators, and literals.

Parser (parser.py): Implements a recursive descent parser to enforce grammar and build the Abstract Syntax Tree (AST).

IR Generator (ir_generator.py): Translates the AST into a flat, three-address-like intermediate representation. This stage handles label generation for jumps and branching.

Executor (ir_executor.py): A stack-based Virtual Machine that simulates a CPU. It manages an operand stack and a symbol table to execute the generated IR instructions.

GUI (gui.py & index.html): A frontend interface to visualize the code execution and output.

🛠️ Tech Stack
Language: Python 3.x

GUI: Web-based (HTML/JS) integration with Python backend.

Pattern: Modular Compiler Design.

🚀 How it Works
Input: User writes high-level code in the GUI.

Compilation: The code is tokenized and parsed into an AST.

Generation: The ir_generator produces a list of instructions (e.g., PUSH 10, STORE x, JMP_IF_FALSE).

Execution: The VM iterates through these instructions, modifying the stack and symbol table in real-time to produce the final output.
