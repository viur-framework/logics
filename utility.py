#-*- coding: utf-8 -*-

def parseInt(value, ret=0):
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


def parseFloat(value, ret=0.0):
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

def optimizeValue(val, allow = [int, bool, float, list, dict, str], default = str):
	"""
	Evaluates the best matching value.
	"""

	if isinstance(val, unicode):
		val = val.encode("utf-8")

	# On string, check if conversion to int or float is possible,
	# if the entire value only consists of digits and does not start
	# with a 0
	if isinstance(val, str):
		if (len(val) > 1 and not val.startswith("0")) or len(val) == 1:
			if all([c in "+-0123456789" for c in val]):
				try:
					val = int(val)
				except ValueError:
					pass

			elif all([c in "+-0123456789." for c in val]):
				try:
					val = float(val)
				except ValueError:
					pass

	if any([isinstance(val, t) for t in allow]):
		return val

	if callable(default):
		return default(val)

	return default
