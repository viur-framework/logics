import os, argparse, json
from logics import Logics
from logics.version import __version__


def main():
    ap = argparse.ArgumentParser(description="ViUR Logics Expressional Language")

    ap.add_argument("expression", type=str, help="The expression to be processed")

    ap.add_argument("-D", "--debug", help="Print debug output", action="store_true")
    ap.add_argument("-e", "--environment", help="Import environment as variables", action="store_true")
    ap.add_argument("-v", "--var", help="Assign variables", action="append", nargs=2, metavar=("var", "value"))
    ap.add_argument("-r", "--run", help="Run expression using interpreter", action="store_true")
    ap.add_argument("-V", "--version", action="version", version="ViUR logics %s" % __version__)

    args = ap.parse_args()
    done = False

    # Try to read input from a file.
    try:
        f = open(args.expression, "rb")
        expr = f.read()
        f.close()

    except IOError:
        expr = args.expression

    vars = {}

    if args.debug:
        print("expr", expr)

    if args.environment:
        vars.update(os.environ)

    # Read variables
    if args.var:
        for var in args.var:
            try:
                f = open(var[1], "rb")
                vars[var[0]] = json.loads(f.read())
                f.close()

            except ValueError:
                vars[var[0]] = None

            except IOError:
                vars[var[0]] = var[1]

    if args.debug:
        print("vars", vars)

    if args.run:
        vili = Logics()
        print(vili.execute(expr, vars, args.debug))

        done = True

    if not done:
        vil = Logics()
        ast = vil.parse(expr)
        if ast:
            ast.dump()


if __name__ == "__main__":
    main()
