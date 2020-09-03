#-*- coding: utf-8 -*-

strType = str #fixme: This is now a relict!


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
		value = strType(value)

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
		value = strType(value)

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

def optimizeValue(val, allow=[int, bool, float, list, dict, str], default=strType):
	"""
	Evaluates the best matching value.
	"""
	# Perform string conversion into float or int, whatever fits best.
	if isinstance(val, str):
		ival = parseInt(val, None) if int in allow else None
		fval = parseFloat(val, None) if float in allow else None

		if str not in allow:
			if ival is not None and fval is not None:
				if float(ival) == fval:
					val = ival
				else:
					val = fval
			elif fval is not None:
				val = fval
		elif fval is not None and str(fval) == val:
			val = fval
		elif ival is not None and str(ival) == val:
			val = ival

	if any([isinstance(val, t) for t in allow]):
		return val

	if callable(default):
		return default(val)

	return default
