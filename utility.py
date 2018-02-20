#-*- coding: utf-8 -*-

def parseInt(s, ret = 0):
	"""
	Parses a value as int
	"""
	if s is None:
		return ret

	if not isinstance(s, str):
		return int(s)

	elif s:
		if s[0] in "+-":
			ts = s[1:]
		else:
			ts = s

		if ts and all([_ in "0123456789" for _ in ts]):
			return int(s)

	return ret

def parseFloat(s, ret = 0.0):
	"""
	Parses a value as float.
	"""
	if s is None:
		return ret

	if not isinstance(s, str):
		return float(s)

	elif s:
		if s[0] in "+-":
			ts = s[1:]
		else:
			ts = s

		if ts and ts.count(".") <= 1 and all([_ in ".0123456789" for _ in ts]):
			return float(s)

	return ret

def optimizeValue(val, allow = [int, bool, float, list, dict, str, unicode], default = str):
	"""
	Evaluates the best matching value.
	"""
	# On string, check if parsing int or float is possible.
	if isinstance(val, str):
		v = parseInt(val, None)
		if v is not None:
			val = v
		else:
			v = parseFloat(val, None)
			if v is not None:
				val = v

	if any([isinstance(val, t) for t in allow]):
		return val

	if callable(default):
		return default(val)

	return default
