import sys
import scanner

hadError = False

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
        print(lines)
    
    run(lines)
    if (hadError):
        sys.exit("Error was detected")


def run_prompt():
    while True:
        data = input("> ")
        if data == None:
            break
        run(data)
        hadError = False


def run(lines: str):
    scanner_instance = scanner.Scanner(lines)
    scanner_instance.scanTokens()


def error(line: int, message: str) -> None:
    report(line, "", message)


def report(line: int, where: str, message: str):
    sys.stderr.write(f'[line + {line} ] Error{where}: {message}')
    hadError = True

if __name__ == "__main__":
    main()
