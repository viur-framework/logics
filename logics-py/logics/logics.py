"""
logics is a domain-specific expression language with a Python-style syntax,
that can be compiled and executed in any of ViUR's runtime contexts.
"""
import typing as t
from .parser import LogicsParser, LogicsNode
from .value import Value, parse_float, parse_int, unescape


_parser = LogicsParser()


class _Stack(list):
    def op0(self, value):
        super().append(Value(value))

    def op1(self, fn):
        self.op0(fn(self.pop()))

    def op2(self, fn):
        b = self.pop()
        self.op0(fn(self.pop(), b))

    def op3(self, fn):
        c = self.pop()
        b = self.pop()
        self.op0(fn(self.pop(), b, c))


class Logics:
    MAX_FOR_ITERATIONS: int = 4 * 1024

    def __init__(self, src: str, debug: bool = False):
        super().__init__()
        self.ast = _parser.parse(src)

        self.functions = {
            "bool": bool,
            # "currency": Logics.lgx_currency,
            "endswith": lambda value, suffix: str(value).endswith(str(suffix)),
            "float": parse_float,
            "int": parse_int,
            "join": lambda value, delimiter=", ": str(delimiter).join(str(item) for item in value.list()),
            "keys": lambda obj: list(obj.dict().keys()),
            "len": len,
            "lfill": lambda value, length, fill=" ": str(value).rjust(int(length), str(fill)),
            "lower": lambda value: str(value).lower(),
            "lstrip": lambda value, chars=" \t\r\n": str(value).lstrip(str(chars)),
            "max": lambda value: max(value),
            "min": lambda value: min(value),
            "range": Logics.lgx_range,
            "replace": Logics.lgx_replace,
            "rfill": lambda value, length, fill=" ": str(value).ljust(int(length), str(fill)),
            "round": lambda value, digits=0: round(float(value), int(digits)),
            "rstrip": lambda value, chars=" \t\r\n": str(value).rstrip(str(chars)),
            "split": lambda value, delimiter=",": str(value).split(str(delimiter)),
            "startswith": lambda value, prefix: str(value).startswith(str(prefix)),
            "str": lambda val: Value(str(val), optimize=False),
            "strip": lambda s, c=" \t\r\n": str(s).strip(str(c)),
            "sum": lambda value: sum(
                [Value.align(item, allow=(bool, int, float), default=parse_int) for item in value]
            ),
            "upper": lambda value: str(value).upper(),
            "values": lambda obj: list(obj.dict().values()),
            # "vars": ... is a special case handled inline!
        }

        self.debug = debug
        if self.debug:
            self.ast.dump()

    @staticmethod
    def lgx_range(start: int, end: int | None = None, step: int | None = None) -> range:
        if step is not None:
            return tuple(range(int(start), int(end), int(step)))
        if end is not None:
            return tuple(range(int(start), int(end)))

        return tuple(range(int(start)))

    @staticmethod
    def lgx_currency(
        value: float,
        decimal_delimiter: str = ",",
        thousands_delimiter: str = ".",
        symbol: str = "€",
    ) -> str:
        ret = f"{value:.2f}"
        before, behind = ret.split(".", 1)
        before = reversed(before)

        ret = ""
        for i, ch in enumerate(before):
            if i > 0 and i % 3 == 0:
                ret = ch + thousands_delimiter + ret
            else:
                ret = ch + ret

        ret = ret + decimal_delimiter + behind

        # append symbol if defined
        if symbol:
            ret += " " + symbol

        return ret.strip()

    @staticmethod
    def lgx_replace(value: str, find: str | list[str] = " ", replace: str = "") -> str:
        # handle a list when passed to replace multiple strings
        if isinstance(find, list):
            for item in find:
                value = lgx_replace(value, i, replace)

            return value

        return str(value).replace(str(find), str(replace))

    def run(self, values: dict = {}) -> Value | None:
        """
        Runs the compiled Logics expression with a given variable set.
        """
        stack = _Stack()
        self._run(self.ast, stack, values)

        try:
            return stack.pop()
        except IndexError:
            return None

    def _run(self, node: LogicsNode, stack: _Stack, values: dict):
        """
        Internal virtual machine working on the recursive
        LogicsNodes, a stack and the values.
        """

        # Use this function to access values
        def _vars(name: t.Optional[str] = None):
            return values.get(str(name)) if name is not None else values

        # Flow operations are being evaluated on demand
        match node.emit:
            case "and" | "or":
                assert len(node.children) == 2
                self._run(node.children[0], stack, values)

                check = stack.pop()
                test = bool(check)
                if node.emit == "or":
                    test = not test

                if test:
                    self._run(node.children[1], stack, values)
                else:
                    stack.append(check)

                return

            case "cmp":
                assert len(node.children) > 1
                self._run(node.children[0], stack, values)

                for node in node.children[1:]:
                    self._run(node.children[0], stack, values)

                    b = stack.pop()
                    a = stack.pop()

                    match node.emit:
                        case "eq":
                            res = a == b
                        case "neq":
                            res = a != b
                        case "lt":
                            res = a < b
                        case "lteq":
                            res = a <= b
                        case "gt":
                            res = a > b
                        case "gteq":
                            res = a >= b
                        case "in":
                            res = a in b
                        case "outer":
                            res = a not in b

                        case node:
                            raise NotImplementedError(f"Logics VM: cmp {node=} is not implemented")

                    if not res:
                        stack.op0(False)
                        return

                    stack.op0(b)

                stack.op0(True)
                return

            case "call":
                fname = node.children[0].match

                if len(node.children) > 1:
                    self._run(node.children[1], stack, values)
                    args = stack.pop().list()
                else:
                    args = ()

                fn = self.functions.get(fname)
                if not fn and fname == "vars":
                    fn = _vars

                if fn:
                    try:
                        stack.op0(fn(*args))
                    except TypeError:
                        # TODO: Improve parameter validation
                        stack.op0(f"#ERR:Invalid call to {fname}()")
                else:
                    stack.op0(f"#ERR:Call to unknown function {fname}()")

                return

            case "comprehension":
                assert len(node.children) in (3, 4)

                # Obtain iterable
                self._run(node.children[2], stack, values)
                items = stack.pop()

                # Extract AST components for faster access
                each = node.children[0]
                name = node.children[1].match
                test = node.children[3] if len(node.children) > 3 else None

                # Loop over the iterator
                ret = []
                for i, item in enumerate(items):
                    # Limit loop to maximum of iterations (#17)
                    if i >= Logics.MAX_FOR_ITERATIONS:
                        break

                    values[name] = item

                    # optional if
                    if test:
                        self._run(test, stack, values)
                        if not bool(stack.pop()):
                            continue

                    self._run(each, stack, values)
                    ret.append(stack.pop())

                stack.op0(ret)
                return

            case "if":
                assert len(node.children) == 3
                # Evaluate condition
                self._run(node.children[1], stack, values)
                # Evaluate specific branch
                self._run(node.children[0 if bool(stack.pop()) else 2], stack, values)
                return

        # Otherwise, traverse any children first (default behavior, except state otherwise above)
        if node.children:
            for child in node.children:
                self._run(child, stack, values)

        # Stack operations (processed post-children)
        match node.emit:
            # Pushing values
            case "False":
                stack.op0(False)
            case "Identifier":
                stack.op0(node.match)
            case "None":
                stack.op0(None)
            case "Number":
                if "." in node.match:
                    stack.op0(parse_float(node.match))
                else:
                    stack.op0(parse_int(node.match))

            case "String":
                stack.op0(unescape(node.match[1:-1]))  # cut "..." from string.
            case "True":
                stack.op0(True)

            # Operations
            case "add":
                stack.op2(lambda a, b: a + b)
            case "attr":
                stack.op2(lambda value, attr: value[attr])
            case "div":
                stack.op2(lambda a, b: a / b)
            case "entity":
                ...  # nothing to do
            case "idiv":
                stack.op2(lambda a, b: a // b)
            case "in":
                stack.op2(lambda a, b: a in b)
            case "invert":
                stack.op1(lambda a: ~a)
            case "list":
                stack.op0(list(reversed([stack.pop() for _ in range(len(node.children))])))
            case "mod":
                stack.op2(lambda a, b: a % b)
            case "mul":
                stack.op2(lambda a, b: a * b)
            case "neg":
                stack.op1(lambda a: -a)
            case "not":
                stack.op1(lambda a: not a)
            case "outer":
                stack.op2(lambda a, b: a not in b)
            case "pos":
                stack.op1(lambda a: +a)
            case "pow":
                stack.op2(lambda a, b: a**b)
            case "index":
                stack.op2(lambda value, idx: value[idx])
            case "load":
                stack.op1(lambda name: _vars() if name == "vars" else _vars(name))
            case "slice":
                # TODO
                # stack.op3(lambda value, from, to: value.__getitem__(from, to))
                pass
            case "strings":
                stack.op0("".join([stack.pop() for _ in range(node.children.length)]))

            case "sub":
                stack.op2(lambda a, b: a - b)

            case node:
                raise NotImplementedError(f"Logics VM: {node=} is not implemented")
