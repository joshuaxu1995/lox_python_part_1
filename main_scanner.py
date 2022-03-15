import sys
import scanner
import tokens as ts
from parser import Parser
import side_code_gen.ast_printer as ast_printer
import resolver
import runtime_error
from interpreter import Interpreter

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

    statements = parser.parse()
    interpreter = Interpreter()

    if (had_error):
        return

    temp_resolver = resolver.Resolver(interpreter)
    temp_resolver.resolve(statements)

    if (had_error):
        return

    interpreter.interpret(statements)


def error_with_line(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str):
    sys.stderr.write(f'[line {line} ] Error{where}: {message}')
    hadError = True


def error(token: ts.Token, message: str):
    if (token == ts.TokenType.EOF):
        report(token.line, " at end", message)
    else:
        report(token.line, " at '" + token.lexeme + "'", message)


def runtime_error(error: runtime_error.RuntimeError):
    sys.stderr.write(f'{error.message} \n[line {error.token.line}]')
    had_runtime_error = True


if __name__ == "__main__":
    main()
