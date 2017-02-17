#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
logics is the attempt of implementing a domain-specific, Python-style expressional language that can be
compiled and executed in any of ViURs runtime contexts.
"""

__author__ = "Jan Max Meyer"
__copyright__ = "Copyright 2015-2017, Mausbrand Informationssysteme GmbH"
__version__ = "0.4"
__license__ = "LGPLv3"
__status__ = "Beta"

import pynetree

def parseInt(s, ret = 0):
	"""
	Parses a value as int
	"""
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

def optimizeValue(val, allow = [int, bool, float, list, dict, str], default = str):
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

class Function(object):
	def __init__(self, call, js):
		if not callable(call):
			raise TypeError("Parameter must be callable")

		self.call = call

		if not isinstance(js, str):
			raise TypeError("Parameter must be str")

		self.js = js


class Parser(pynetree.Parser):

	functions = None

	def __init__(self):
		super(Parser, self).__init__(
			"""
			%skip		    /\\s+|#.*\n/;

			@IDENT		    /[A-Za-z_][A-Za-z0-9_]*/;
			@STRING 	    /"[^"]*"|'[^']*'/;
			@NUMBER 	    /[0-9]+\.[0-9]*|[0-9]*\.[0-9]+|[0-9]+/;

			logic$          : expression
							;

			expression      : test ;

			test   	        : if_else
							| or_test
							;

			@if_else        : or_test 'if' or_test 'else' test
							;

			or_test		    : @( and_test ( 'or' and_test )+ )
							| and_test
							;

			and_test	    : @( not_test ( 'and' not_test )+ )
							| not_test
							;

			not_test	    : @( 'not' not_test )
							| comparison
							;

			comparison	    : @(expr ( ( "==" | ">=" | "<=" | "<" | ">" | "<>" | "!="
											| @in( 'in' ) | @not_in( 'not' 'in' ) ) expr)+ )
							| expr
							;

			expr		    : @add( expr '+' term )
							| @sub( expr '-' term )
							| term
							;

			term		    : @mul( term '*' factor )
							| @div( term '/' factor )
							| @mod( term '%' factor )
							| factor;

			factor		    : @( ( "+" | "-" | "~" ) factor)
							| power
							;

			power		    : @(entity "**" factor)
							| entity
							;

			entity          : @( atom trailer+ )
							| atom
							;

			trailer         : '(' list ')' | '[' expression ']' | '.' IDENT ;

			atom		    : ( "True" | "False" )
							| NUMBER
							| IDENT
							| @strings( STRING+ )
							| comprehension
							| '[' list ']'
							| @( '(' expression ')' )
							;

			@comprehension  : '[' expression 'for' IDENT 'in' expression ( 'if' expression )? ']'
							;


			@list           : expression (',' expression )*
			                |
			                ;
			""")

		self.functions = {}

		self.functions["upper"] = Function(
			lambda x: str.upper(x),
			"return String(arguments[0]).toUpperCase();"
		)

		self.functions["lower"] = Function(
			lambda x: str.lower(x),
		    "return String(arguments[0]).toLowerCase();"
		)

		self.functions["str"] = Function(
			lambda x: str(x),
		    "return String(arguments[0]);"
		)

		self.functions["int"] = Function(
			lambda x: int(x),
		    "return parseInt(arguments[0]);"
		)

		self.functions["float"] = Function(
			lambda x: float(x),
		    "return parseFloat(arguments[0]);"
		)

		self.functions["len"] = Function(
			lambda x: len(x),
		    "return arguments[0].length;"
		)

		self.functions["sum"] = Function(
			lambda v: sum([optimizeValue(_, allow=[bool, int, float], default=0) for _ in v]),
		    "return arguments[0].length;"   # fixme JavaScript
		)
		self.functions["max"] = Function(
			lambda v: max(v),
		    "return arguments[0].length;" # fixme JavaScript
		)

		self.functions["min"] = Function(
			lambda v: min(v),
		    "return arguments[0].length;" # fixme JavaScript
		)

		self.functions["join"] = Function(
			lambda l, d: str(d).join(l),
		    "return arguments[0].length;" # fixme JavaScript
		)


	def compile(self, src):
		return self.parse(src)


class JSCompiler(Parser):
	"""
	Compiler to emit viurLogics code as JavaScript code.
	"""
	stack = None

	def __init__(self):
		super(JSCompiler, self).__init__()
		self.apiPrefix = "viurLogics"

	def compile(self, src, fields = None):
		self.stack = []

		t = self.parse(src)
		if not t:
			return None

		#self.dump(t)
		self.traverse(t)

		return self.stack.pop()

	def api(self):
		"""
		Generates the portion of native JavaScript code required to implement
		the semantics of the viurLogic language on pure JavaScript side.

		:return: JavaScript code.
		"""

		s = str()

		# GetField ------------------------------------------------------------
		s += "function %sGetField(name)\n" % self.apiPrefix
		s += """{
	return document.getElementsByName(name)[0].value;
}

"""

		# Add -----------------------------------------------------------------
		s += "function %sAdd(a, b)\n" % self.apiPrefix
		s += """{
	if( typeof a == "string" || typeof b == "string" )
		return String(a) + String(b);

	if( typeof a != "number" )
		a = a ? 1 : 0;
	if( typeof b != "number" )
		b = b ? 1 : 0;

	return a + b;
}

"""
		# Sub -----------------------------------------------------------------
		s += "function %sSub(a, b)\n" % self.apiPrefix
		s += """{
	if( typeof a != "number" )
		a = a ? 1 : 0;
	if( typeof b != "number" )
		b = b ? 1 : 0;

	return a - b;
}

"""
		# Mul -----------------------------------------------------------------
		s += "function %sMul(a, b)\n" % self.apiPrefix
		s += """{
	if( typeof a == "string" || typeof b == "string" )
	{
		var cnt = 0;
		var bs = "";
		if( typeof a == "number" )
		{
			cnt = a;
			bs = b;
		}
		else if( typeof b == "number" )
		{
			cnt = b;
			bs = a;
		}

		var s = "";
		while( cnt-- > 0 )
			s += bs;

		return s;
	}

	if( typeof a != "number" )
		a = a ? 1 : 0;
	if( typeof b != "number" )
		b = b ? 1 : 0;

	return a * b;
}

"""

		# Div -----------------------------------------------------------------
		s += "function %sDiv(a, b)\n" % self.apiPrefix
		s += """{
	if( typeof a != "number" )
		a = typeof a == "boolean" ? (a ? 1 : 0) : 0;
	if( typeof b != "number" )
		b = typeof b == "boolean" ? (b ? 1 : 0) : 0;

	return a / b;
}

"""

		# In ------------------------------------------------------------------
		s += "function %sIn(a, b)\n" % self.apiPrefix
		s += """{
	try
	{
		return b.indexOf(a) > -1 ? true : false;
	}
	catch(e)
	{
		return false;
	}
}

"""

		for f, o in self.functions.items():
			s += "function %s_%s()\n{\n\t%s\n}\n\n" % (self.apiPrefix, f, o.js)

		return s

	def post_if_else(self, node):
		alt = self.stack.pop()
		expr = self.stack.pop()
		res = self.stack.pop()

		self.stack.append("%s ? %s : %s" % (expr, res, alt))

	def post_or_test(self, node):
		for i in range(1, len(node.children)):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append("%s || %s" % (l, r))

	def post_and_test(self, node):
		for i in range(1, len(node.children)):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append("%s && %s" % (l, r))

	def post_not_test(self, node):
		self.stack.append("!%s" % self.stack.pop())

	def post_comparison(self, node):
		for i in range(1, len(node.children), 2):
			op = node.children[i].symbol
			r = self.stack.pop()
			l = self.stack.pop()

			if op == "in":
				self.stack.append("%sIn(%s, %s)" % (self.apiPrefix, l, r))
			elif op == "not_in":
				self.stack.append("!%sIn(%s, %s)" % (self.apiPrefix, l, r))
			else:
				if op == "<>":
					op = "!="

				self.stack.append("%s %s %s" % (l, op, r))

	def post_add(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%sAdd(%s, %s)" % (self.apiPrefix, l, r))

	def post_sub(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%sSub(%s, %s)" % (self.apiPrefix, l, r))

	def post_mul(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%sMul(%s, %s)" % (self.apiPrefix, l, r))

	def post_div(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%sDiv(%s, %s)" % (self.apiPrefix, l, r))

	def post_mod(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%sMod(%s, %s)" % (self.apiPrefix, l, r))

	def post_factor(self, node):
		op = self.stack.pop()

		if isinstance(op, (str, unicode)):
			self.stack.append(op)
		elif node[1][0][0] == "+":
			self.stack.append("+(%s)" % op)
		elif node[1][0][0] == "-":
			self.stack.append("-(%s)" % op)
		else:
			self.stack.append("~(%s)" % op)

	def post_atom(self, node):
		self.stack.append("(%s)" % self.stack.pop())

	def post_call(self, node):
		func = node.children[0].match

		l = []
		for i in range(1, len(node.children)):
			l.append(self.stack.pop())

		if not func in self.functions.keys():
			return

		l.reverse()
		self.stack.append("%s_%s(%s)" % (self.apiPrefix, func, ", ".join(l)))

	def post_path(self, node):
		#fixme
		name = node.children[0].match
		if name in ["True", "False"]:
			self.stack.append(name.lower())
		else:
			self.stack.append("%sGetField(\"%s\")" % (self.apiPrefix, name))

	def post_STRING(self, node):
		self.stack.append("\"%s\"" % node.match[1:-1])

	def post_strings(self, node):
		s = ""
		for i in range(len(node.children)):
			s = str(self.stack.pop()[1:-1]) + s

		self.stack.append("\"%s\"" % s)

	def post_list(self, node):
		l = []
		for i in range(0, len(node.children)):
			l.append(self.stack.pop())

		l.reverse()
		self.stack.append("Array(" + ", ".join(l) + ")")

	def post_NUMBER(self, node):
		self.stack.append(node.match)



class Interpreter(Parser):
	"""
	Interpreter class for the viurLogics.
	"""

	def __init__(self):
		super(Interpreter, self).__init__()
		self.stack = []
		self.fields = {}
		self.prefix = ""

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
				self.dump(t)
		else:
			t = src

		self.traverse(t)
		return self.stack.pop() if self.stack else None

	def traverse(self, node, prePrefix = "pre_", passPrefix = "pass_", postPrefix = "post_", *args, **kwargs):
		"""
		Modified AST traversal function.
		"""
		def perform(prefix, loop = None, *args, **kwargs):
			if loop is not None:
				kwargs["_loopIndex"] = loop

			for x in range(0, 2):
				if x == 0:
					fname = "%s%s" % (prefix, node.emit or node.symbol)
				else:
					if node.rule is None:
						break

					fname = "%s%s_%d" % (prefix, node.emit or node.symbol, node.rule)

				if fname and fname in dir(self) and callable(getattr(self, fname)):
					getattr(self, fname)(node, *args, **kwargs)
					return True

				elif loop is not None:
					fname += "_%d" % loop

					if fname and fname in dir(self) and callable(getattr(self, fname)):
						getattr(self, fname)(node, *args, **kwargs)
						return True

			return False

		if node is None:
			return

		if isinstance(node, pynetree.Node):
			# Don't run through the AST in case of "comprehension" or "entity".
			if (node.emit or node.symbol) not in ["comprehension", "entity"]:
				# Pre-processing function
				perform(prePrefix, *args, **kwargs)

				for cnt, i in enumerate(node.children):
					self.traverse(i, prePrefix, passPrefix, postPrefix, *args, **kwargs)

					# Pass-processing function
					perform(passPrefix, loop=cnt, *args, **kwargs)

			# Post-processing function
			if not perform(postPrefix, *args, **kwargs):
				# Allow for post-process function in the emit info.
				if callable(self.emits[node.key]):
					self.emits[node.key](node, *args, **kwargs)
				elif self.emits[node.key]:
					print(self.emits[node.key])

		elif isinstance(node, list):
			for item in node:
				self.traverse(item, prePrefix, passPrefix, postPrefix, *args, **kwargs)

		else:
			raise ValueError()

	# Traversal functions

	def post_comprehension(self, node):
		#print("COMPREHENSION")
		#print("COMPREHENSION", "begin", self.stack)
		#self.dump(node.children[2])

		self.traverse(node.children[2])
		iter = self.stack.pop()

		#print(iter)

		ret = []
		ofields = self.fields
		self.fields = tfields = self.fields.copy()

		for var in iter or []:
			tfields[self.prefix + node.children[1].match] = var

			if len(node.children) == 4:
				self.traverse(node.children[3])

				if not self.stack.pop():
					continue

			self.traverse(node.children[0])
			ret.append(self.stack.pop())

		self.fields = ofields
		self.stack.append(ret)

		#print("COMPREHENSION", "end", self.stack)

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

			if tail.symbol == "IDENT":

				# fixme: This is *not* the desired behavior!
				# Later it must be checked which object-related functions
				# are allowed to be called from logics.
				if tail.match in dir(value):
					value = getattr(value, tail.match)

				elif isinstance(value, dict) and tail.match in value.keys():
					value = value[tail.match]

				continue
			else:
				self.traverse(tail)
				tail = self.stack.pop()

				#print("entity", value, tail)

			#print("OK", value, tail)

			if callable(value):
				#print("entity", value, tail)
				try:
					value = value(*tail)
				except:
					#raise
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
				self.stack.append(l in r)
			elif op == "not_in":
				self.stack.append(l not in r)

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

	def post_call(self, node):
		func = node.children[0].match

		l = []
		for i in range(1, len(node.children)):
			l.append(self.stack.pop())

		if not func in self.functions.keys():
			return

		self.stack.append(self.functions[func].call(*reversed(l)))

	def post_IDENT(self, node):
		var = self.prefix + node.match

		if var in self.fields:
			self.stack.append(optimizeValue(self.fields[var]) if self.fields[var] is not None else None)
		elif node.match in self.functions:
			self.stack.append(self.functions[node.match].call)
		else:
			self.stack.append(None)

	def post_NUMBER(self, node):
		self.stack.append(optimizeValue(node.match, allow=[int, float], default=0))

	def post_STRING(self, node):
		self.stack.append(node.match[1:-1])

	def post_strings(self, node):
		s = ""
		for i in range(len(node.children)):
			s = str(self.stack.pop()) + s

		self.stack.append(s)

	def post_list(self, node):
		l = []
		for i in range(0, len(node.children)):
			l.append(self.stack.pop())

		l.reverse()

		self.stack.append(l)


if __name__ == "__main__":
	import argparse

	ap = argparse.ArgumentParser(description="ViUR Logics Expressional Language")

	ap.add_argument("expression", type=str, help="The expression to compile")

	ap.add_argument("-D", "--debug", help="Print debug output", action="store_true")
	ap.add_argument("-e", "--environment", help="Import environment as variables", action="store_true")
	ap.add_argument("-v", "--var",  help="Assign variables",
	                action="append", nargs=2, metavar=("var", "value"))
	ap.add_argument("-r", "--run", help="Run expression using interpreter",
	                action="store_true")

	ap.add_argument("-j", "--javascript", help="Compile expression to JavaScript",
	                action="store_true")
	ap.add_argument("-J", "--javascript+api", help="Compile expression to JavaScript with API",
	                action="store_true")
	ap.add_argument("-V", "--version", action="version", version="ViUR logics %s" % __version__)

	args = ap.parse_args()
	expr = args.expression
	done = False

	vars = {}

	if args.debug:
		print("expr", expr)

	if args.environment:
		import os
		vars.update(os.environ)

	# Read variables
	if args.var:
		for var in args.var:
			vars[var[0]] = var[1]

	if args.debug:
		print("vars", vars)

	if args.run:
		vili = Interpreter()
		print(vili.execute(expr, vars, args.debug))

		done = True

	if args.javascript or getattr(args, "javascript+api"):
		viljs = JSCompiler()

		if getattr(args, "javascript+api"):
			print(viljs.api())

		print(viljs.compile(expr))

		done = True

	if not done:
		vil = Parser()
		ast = vil.parse(expr)
		vil.dump(ast)
