import os
import argparse
import json
from logics import Logics
from logics.version import __version__


def main():
    ap = argparse.ArgumentParser(description="Logics")

    ap.add_argument("expression", type=str, help="Expression to be parsed and executed")

    ap.add_argument("-v", "--var", help="Assign variables", action="append", nargs=2, metavar=("var", "value"))
    ap.add_argument("-V", "--version", action="version", version="Logics %s" % __version__)

    args = ap.parse_args()

    # Try to read input from a file.
    try:
        f = open(args.expression, "rb")
        expr = f.read()
        f.close()

    except IOError:
        expr = args.expression

    vars = dict(os.environ)

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

    logics = Logics(expr)
    print(logics.run(vars))


if __name__ == "__main__":
    main()
