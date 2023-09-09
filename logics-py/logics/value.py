MAX_STRING_LENGTH: int = 32 * 1024


def parse_int(value, ret=0):
    """
    Parses a value as int.

    This function works similar to its JavaScript-pendant, and performs
    checks to parse most of a string value as integer.

    :param value: The value that should be parsed as integer.
    :param ret: The default return value if no integer could be parsed.

    :return: Either the parse value as int, or ret if parsing not possible.
    """
    if value is None:
        return ret

    if not isinstance(value, str):
        value = str(value)

    conv = ""
    value = value.lstrip()

    for ch in value:
        if ch not in "+-0123456789":
            break

        conv += ch

    try:
        return int(conv)
    except ValueError:
        return ret


def parse_float(value, ret=0.0):
    """
    Parses a value as float.

    This function works similar to its JavaScript-pendant, and performs
    checks to parse most of a string value as float.

    :param value: The value that should be parsed as float.
    :param ret: The default return value if no integer could be parsed.

    :return: Either the parse value as float, or ret if parsing not possible.
    """
    if value is None:
        return ret

    if not isinstance(value, str):
        value = str(value)

    conv = ""
    value = value.lstrip()
    dot = False

    for ch in value:
        if ch not in "+-0123456789.":
            break

        if ch == ".":
            if dot:
                break

            dot = True

        conv += ch

    try:
        return float(conv)
    except ValueError:
        return ret


class Value:
    def __init__(self, value=None, allow=(int, bool, float, list, dict, str), default=None, optimize=True):
        if value is None:
            self.value = None
            return
        elif isinstance(value, Value):
            self.value = value.value
            return

        assert allow  # allow must not be empty!

        if not optimize and any([isinstance(value, t) for t in allow]):
            self.value = value
            return

        # Perform string conversion into float or int, whatever fits best.
        if isinstance(value, str):
            ival = parse_int(value, None) if int in allow else None
            fval = parse_float(value, None) if float in allow else None

            if fval is not None and str(fval) == value:
                value = fval
            elif ival is not None and str(ival) == value:
                value = ival

        # When a float fits into an int, store it as int
        if isinstance(value, float) and float in allow and int in allow:
            ival = int(value)
            if float(ival) == value:
                value = ival

        if default is None:
            default = allow[-1]  # use last type of allow as default!

        assert default is not None

        if any(isinstance(value, t) for t in allow):
            self.value = value
        elif callable(default):
            self.value = default(value)
        else:
            self.value = default

    def type(self):
        return type(self.value).__name__

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)

    def __bool__(self):
        return bool(self.value)

    def __int__(self):
        if self.type() == "str":
            return parse_int(self.value)
        elif self.value is None:
            return 0

        return int(self.value)

    def __float__(self):
        if self.type() == "str":
            return parse_float(self.value)
        elif self.value is None:
            return 0.0

        return float(self.value)

    def __len__(self):
        if self.type() in ("dict", "list", "str"):
            return len(self.value)

        return len(str(self))

    def __contains__(self, item):
        if self.type() in ("dict", "list"):
            value = Value(item)
            return value.value in self

        return str(item) in str(self)

    def __getitem__(self, item):
        if self.type() == "dict":
            if isinstance(item, slice):
                return Value(None)

            return self.value.get(item)

        value = self.value if self.type() == "list" else str(self)
        return value[item]

    def __iter__(self):
        value = self.value if self.type() in ("dict", "list") else [self]
        return iter(value)

    def __eq__(self, other):
        return self.value == Value(other).value

    def __ne__(self, other):
        return self.value != Value(other).value

    def __compare(self, op, other):
        value = self.value
        other = Value(other).value

        try:
            match op:
                case "lt":
                    return value < other
                case "gt":
                    return value > other
                case "le":
                    return value <= other
                case "ge":
                    return value >= other
                case _:
                    raise NotImplemented(f"Operator {op!r} not implemented")

        except TypeError:
            return False

    def __lt__(self, other):
        return self.__compare("lt", other)

    def __gt__(self, other):
        return self.__compare("gt", other)

    def __le__(self, other):
        return self.__compare("le", other)

    def __ge__(self, other):
        return self.__compare("ge", other)

    def __add__(self, other):
        other = Value(other)
        match self.type(), other.type():
            case ("str", _) | (_, "str"):
                return Value(str(self) + str(other))
            case ("float", _) | (_, "float"):
                return Value(float(self) + float(other))
            case _:
                return Value(int(self) + int(other))

    def __sub__(self, other):
        other = Value(other)
        match self.type(), other.type():
            case ("float", _) | (_, "float"):
                return Value(float(self) - float(other))
            case _:
                return Value(int(self) - int(other))

    def __mul__(self, other):
        other = Value(other)
        match self.type(), other.type():
            case ("str", _) | (_, "str"):
                if self.type() == "str":
                    repeat = str(self)
                    count = int(other)
                else:
                    repeat = str(other)
                    count = int(self)

                # Limit to maximum length of generated string (#18)
                if count * len(repeat) > MAX_STRING_LENGTH:
                    return Value(f"#ERR limit of {MAX_STRING_LENGTH} reached")

                return Value(count * repeat)

            case ("float", _) | (_, "float"):
                return Value(float(self) * float(other))

            case _:
                return Value(int(self) * int(other))

    def __truediv__(self, other):
        other = Value(other)
        match self.type(), other.type():
            case ("float", _) | (_, "float"):
                if not (other := float(other)):
                    return Value("#ERR:division by zero")

                return Value(float(self) / other)
            case _:
                if not (other := int(other)):
                    return Value("#ERR:division by zero")

                return Value(int(self) / other)

    def __floordiv__(self, other):
        other = Value(other)
        if not (other := int(other)):
            return Value("#ERR:division by zero")

        return Value(int(self) // other)

    def __mod__(self, other):
        other = Value(other)
        match self.type(), other.type():
            case ("float", _) | (_, "float"):
                if not (other := float(other)):
                    return Value("#ERR:modulo by zero")

                return Value(float(self) % other)
            case _:
                if not (other := int(other)):
                    return Value("#ERR:modulo by zero")

                return Value(int(self) % other)

    def __pow__(self, other):
        other = Value(other)
        match self.type(), other.type():
            case ("float", _) | (_, "float"):
                return Value(float(self) ** float(other))
            case _:
                return Value(int(self) ** int(other))

    def __pos__(self):
        if self.type() == "float":
            return Value(+float(self))

        return Value(+int(self))

    def __neg__(self):
        if self.type() == "float":
            return Value(-float(self))

        return Value(-int(self))

    def __invert__(self):
        return Value(~int(self))
