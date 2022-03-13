import sys
import scanner
import tokens as ts
from parser import Parser
import ast_printer
from interpreter import RuntimeError, Interpreter

had_error = False
had_runtime_error = False

def main():
    if (len(sys.argv) > 2):
        print("Usage: plox [script]")
    elif (len(sys.argv) == 2):
        run_file(sys.argv[1])
    else:
        run_prompt()


def run_file(path: str):
    lines = None
    with open(path) as f:
        lines = f.read()
    
    run(lines)
    if (had_error):
        sys.exit("Error was detected")
    if (had_runtime_error):
        sys.exit("Runtime error was detected")

def run_prompt():
    while True:
        data = input("> ")
        if data == None:
            break
        run(data)
        hadError = False


def run(lines: str):
    scanner_instance = scanner.Scanner(lines)
    tokens = scanner_instance.scanTokens()

    parser = Parser(tokens)

    expression = parser.parse()

    if (had_error):
        return
    
    interpreter = Interpreter()
    interpreter.interpret(expression)

def error(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str):
    sys.stderr.write(f'[line + {line} ] Error{where}: {message}')
    hadError = True

def error(token: ts.Token, message: str):
    if (token == ts.TokenType.EOF):
        report(token.line, " at end", message)
    else:
        report(token.line, " at '" + token.lexeme + "'", message)

def runtime_error(error: RuntimeError):
    sys.stderr.write(f'{error.message} \n[line {error.token.line}]')
    had_runtime_error = True


if __name__ == "__main__":
    main()
