#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
logics is a domain-specific expressional language with a Python-styled syntax,
that can be compiled and executed in any of ViUR's runtime contexts.
"""

__author__ = "Jan Max Meyer"
__copyright__ = "Copyright 2015-2018 by Mausbrand Informationssysteme GmbH"
__version__ = "2.3"
__license__ = "LGPLv3"
__status__ = "Beta"

import parser
from utility import parseInt, parseFloat, optimizeValue

try:
	# Test if we are in a PyJS environment
	import __pyjamas__
	_pyjsCompat = True

except ImportError:
	_pyjsCompat = False

class Parser(parser.Parser):

	def __init__(self):
		super(Parser, self).__init__()

	def compile(self, src):
		return self.parse(src)

	def traverse(self, node, obj = None, prePrefix = "pre_", passPrefix = "pass_",
					postPrefix = "post_", loopPrefix = "loop_",
						*args, **kwargs):
		"""
		Generic AST traversal function.

		This function allows to walk over the generated abstract syntax tree created by
		:meth:`parser.Parser.parse()` and calls functions before, to loop, by iterating over
		and after the node are walked.

		:param node: The tree node to traverse.
		:param obj: Object to traverse functions from, defaults to self.
		:param prePrefix: Prefix for pre-processed functions, named prePrefix + emit.
		:param passPrefix: Prefix for functions processed by passing though children, named passPrefix + emit.
		:param postPrefix: Prefix for post-processed functions, named postPrefix + emit.
		:param loopPrefix: Prefix for loop-processing functions, named loopPrefix + emit.

		:param args: Arguments passed to these functions as *args.
		:param kwargs: Keyword arguments passed to these functions as **kwargs.
		"""
		if obj is None:
			obj = self

		def perform(prefix, loop = None, *args, **kwargs):
			if not node.emit:
				return False

			if loop is not None:
				kwargs["_loopIndex"] = loop

			fname = "%s%s" % (prefix, node.emit or node.symbol)

			if fname and fname in dir(obj) and callable(getattr(obj, fname)):
				getattr(obj, fname)(node, *args, **kwargs)
				return True

			elif loop is not None:
				fname += "_%d" % loop

				if fname and fname in dir(obj) and callable(getattr(obj, fname)):
					getattr(obj, fname)(node, *args, **kwargs)
					return True

			return False

		# Pre-processing function
		perform(prePrefix, *args, **kwargs)

		# Loop-over function
		if not perform(loopPrefix, *args, **kwargs):

			# Run through the children.
			for count, child in enumerate(node.children):
				self.traverse(child, obj, prePrefix, passPrefix, postPrefix,
								loopPrefix, *args, **kwargs)

				# Pass-processing function
				perform(passPrefix, loop=count, *args, **kwargs)

		# Post-processing function
		perform(postPrefix, *args, **kwargs)


class Interpreter(Parser):
	"""
	Interpreter class for the viurLogics.
	"""

	def __init__(self):
		super(Interpreter, self).__init__()
		self.stack = []
		self.fields = {}
		self.prefix = ""

		self.functions = {}

		self.addFunction("upper", lambda x: str(x).upper())
		self.addFunction("lower", lambda x: str(x).lower())
		self.addFunction("bool", lambda x: bool(x))
		self.addFunction("str", lambda x: str(x))
		self.addFunction("int", lambda x: parseInt(parseFloat(x)))
		self.addFunction("float", parseFloat)
		self.addFunction("len", lambda x: len(x))
		self.addFunction("sum", lambda v: sum([optimizeValue(_, allow=[bool, int, float], default=0) for _ in v]))
		self.addFunction("max", lambda x: max(x))
		self.addFunction("min", lambda x: min(x))

		def _pyjsLogicsJoin(l, d = ", "):
			ret = ""
			for i in l:
				ret += str(i)
				if i is not l[-1]:
					ret += str(d)

			return ret

		self.addFunction("join", _pyjsLogicsJoin if _pyjsCompat else lambda l, d = ", ": str(d).join(l))
		self.addFunction("split", lambda s, d=" ": s.split(d))

	def addFunction(self, name, fn = None):
		"""
		Adds a user-defined function.
		:param name: Name of the function, or the function pointer.
		:param fn: Function pointer, or None. If None, the functions' name will be evolved from the name as fn.
		"""

		if fn is None:
			fn = name
			name = fn.__name__

		assert isinstance(name, str)
		assert callable(fn)

		self.functions[name] = fn

	def getOperands(self, onlyNumeric = True):
		r = self.stack.pop()
		l = self.stack.pop()

		if onlyNumeric:
			l = optimizeValue(l, allow = [bool, int, float], default=0)
			r = optimizeValue(r, allow = [bool, int, float], default=0)
		else:
			l = optimizeValue(l, default=0)
			r = optimizeValue(r, default=0)

		return l, r

	def execute(self, src, fields = None, dump = False, prefix = None):
		self.fields = fields or {}
		self.prefix = prefix or ""

		if isinstance(src, str):
			t = self.compile(src)
			if t is None:
				return None

			if dump:
				t.dump()
		else:
			t = src

		self.traverse(t)
		return self.stack.pop() if self.stack else None

	# Traversal functions

	def loop_comprehension(self, node):
		pass # Do nothing

	def post_comprehension(self, node):
		#print("COMPREHENSION")
		#print("COMPREHENSION", "begin", self.stack)
		#self.dump(node.children[2])

		nexpr = node.children[0]
		nvar = node.children[1]
		niter = node.children[2]
		nif = node.children[3] if len(node.children) > 3 else None

		self.traverse(niter)
		iterator = self.stack.pop()

		#print(iterator)

		ret = []
		ofields = self.fields
		self.fields = tfields = self.fields.copy()

		for var in iterator or []:
			tfields[self.prefix + nvar.match] = var

			if nif:
				self.traverse(nif)

				if not self.stack.pop():
					continue

			self.traverse(nexpr)
			ret.append(self.stack.pop())

		self.fields = ofields
		self.stack.append(ret)

		#print("COMPREHENSION", "end", self.stack)

	def loop_entity(self, node):
		pass # Do nothing

	def post_entity(self, node):
		#print("entity %d" % self.call_entity)
		#self.dump(node)

		self.traverse(node.children[0])
		value = self.stack.pop()
		#print("entity", value)

		for i, tail in enumerate(node.children[1:]):
			#print("ENTITY", type(value), i, tail.symbol, tail.match)
			if value is None:
				break

			if tail.emit == "IDENT":
				# Expand list into its first entry when expansion is continued here.
				if isinstance(value, list): # and len(value) == 1:
					value = value[0]

				# Dive into dict by key
				if isinstance(value, dict):
					value = value.get(tail.match)

				continue
			else:
				self.traverse(tail)
				tail = self.stack.pop()

				#print("entity", value, tail)

			#print("OK", value, tail)
			if callable(value):
				try:
					value = value(*tail)

				except:
					value = None
			else:
				try:
					value = value[tail]

				except:
					value = None

		self.stack.append(value)

	# Evaluational-depending traversal functions

	def post_if_else(self, node):
		alt = self.stack.pop()
		expr = self.stack.pop()
		res = self.stack.pop()

		self.stack.append(res if expr else alt)

	def post_or_test(self, node):
		for i in range(1, len(node.children)):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append(l or r)

	def post_and_test(self, node):
		for i in range(1, len(node.children)):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append(l and r)

	def post_not_test(self, node):
		self.stack.append(not self.stack.pop())

	def post_comparison(self, node):
		for i in range(1, len(node.children), 2):
			op = node.children[i].emit or node.children[i].symbol

			r = self.stack.pop()
			l = self.stack.pop()

			if op == "<":
				self.stack.append(l < r)
			elif op == ">":
				self.stack.append(l > r)
			elif op == "==":
				self.stack.append(l == r)
			elif op == ">=":
				self.stack.append(l >= r)
			elif op == "<=":
				self.stack.append(l <= r)
			elif op == "<>" or op == "!=":
				self.stack.append(l != r)

			elif op == "in":
				try:
					self.stack.append(l in r)
				except:
					self.stack.append(False)

			elif op == "not_in":
				try:
					self.stack.append(l not in r)
				except:
					self.stack.append(False)

	def post_add(self, node):
		l, r = self.getOperands(False)

		if isinstance(l, str) or isinstance(r, str):
			if not isinstance(l, str):
				l = str(l)
			else:
				r = str(r)

		#print("add", type(l), l, type(r), r)
		self.stack.append(l + r)

	def post_sub(self, node):
		l, r = self.getOperands()

		#print("sub", type(l), l, type(r), r)
		self.stack.append(l - r)

	def post_mul(self, node):
		l, r = self.getOperands(False)

		if isinstance(l, str) and isinstance(r, str):
			r = 0
		elif isinstance(l, str) or isinstance(r, str):
			if parseInt(l, None) is not None:
				l = int(l)
			elif parseInt(r, None) is not None:
				r = int(r)

		#print("mul", type(l), l, type(r), r)
		self.stack.append(l * r)

	def post_div(self, node):
		l, r = self.getOperands()

		#print("div", type(l), l, type(r), r)
		self.stack.append(l / r)

	def post_mod(self, node):
		l, r = self.getOperands()

		#print("mod", type(l), l, type(r), r)
		self.stack.append(l % r)

	def post_factor(self, node):
		op = self.stack.pop()
		#print("factor", op)

		if isinstance(op, str) or isinstance(op, unicode):
			self.stack.append(op)
		elif node.children[0].match == "+":
			self.stack.append(+op)
		elif node.children[0].match == "-":
			self.stack.append(-op)
		else:
			self.stack.append(~op)

	def post_True(self, node):
		self.stack.append(True)

	def post_False(self, node):
		self.stack.append(False)

	def post_IDENT(self, node):
		var = self.prefix + node.match

		if var in self.fields:
			self.stack.append(optimizeValue(self.fields[var]) if self.fields[var] is not None else None)
		elif node.match in self.functions:
			self.stack.append(self.functions[node.match])
		else:
			self.stack.append(None)

	def post_NUMBER(self, node):
		self.stack.append(optimizeValue(node.match, allow=[int, float], default=0))

	def post_STRING(self, node):
		def replaceEscapeStrings(s):
			for seq, ch in {
				"n": "\n",
				"r": "\r",
				"t": "\t",
				"v": "\v",
				"\"": "\"",
				"\'": "\'",
				"\\": "\\"
			}.items():
				s = s.replace("\\%s" % seq, ch)

			return s

		self.stack.append(replaceEscapeStrings(str(node.match[1:-1])))

	def post_strings(self, node):
		s = ""
		for _ in range(len(node.children)):
			s = str(self.stack.pop()) + s

		self.stack.append(s)

	def post_list(self, node):
		l = []
		for _ in range(0, len(node.children)):
			l.append(self.stack.pop())

		l.reverse()

		self.stack.append(l)


if __name__ == "__main__":
	import argparse, json

	ap = argparse.ArgumentParser(description="ViUR Logics Expressional Language")

	ap.add_argument("expression", type=str, help="The expression to be processed")

	ap.add_argument("-D", "--debug", help="Print debug output", action="store_true")
	ap.add_argument("-e", "--environment", help="Import environment as variables", action="store_true")
	ap.add_argument("-v", "--var",  help="Assign variables", action="append", nargs=2, metavar=("var", "value"))
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
		import os
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
		vili = Interpreter()
		print(vili.execute(expr, vars, args.debug))

		done = True

	if not done:
		vil = Parser()
		ast = vil.parse(expr)
		if ast:
			ast.dump()
