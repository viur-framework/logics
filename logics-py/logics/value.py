
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
	value = value.strip()

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
	value = value.strip()
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
	def __init__(self, value=None, allow=(int, bool, float, list, dict, str), default=None, optimize=False):
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

		if any([isinstance(value, t) for t in allow]):
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
		return self.value

	def __int__(self):
		return parse_int(self.value)

	def __float__(self):
		return parse_float(self.value)

	def __add__(self, op):
		match self.type(), op.type():
			case ("str", _) | (_, "str"):
				return Value(str(self) + str(op))
			case ("float", _) | (_, "float"):
				return Value(float(self) + float(op))
			case _:
				return Value(int(self) + int(op))

	def __sub__(self, op):
		match self.type(), op.type():
			case ("float", _) | (_, "float"):
				return Value(float(self) - float(op))
			case _:
				return Value(int(self) - int(op))

	def __mul__(self, op):
		match self.type(), op.type():
			case ("str", _):
				return Value(str(self) * int(op))
			case (_, "str"):
				return Value(int(self) * str(op))
			case ("float", _) | (_, "float"):
				return Value(float(self) * float(op))
			case _:
				return Value(int(self) * int(op))

	def __truediv__(self, op):
		match self.type(), op.type():
			case ("float", _) | (_, "float"):
				return Value(float(self) / float(op))
			case _:
				return Value(int(self) / int(op))


print(repr(Value("4112")))
print(repr(Value("4112", optimize=True)))
