#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
logics is the attempt of implementing a domain-specific, Python-style expressional language that can be
compiled and executed in any of ViURs runtime contexts.
"""

__author__ = "Jan Max Meyer"
__copyright__ = "Copyright 2015-2017, Mausbrand Informationssysteme GmbH"
__version__ = "0.4"
__license__ = "GPLv3"
__status__ = "Beta"

import pynetree

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

			logic$          : evaluation
							;

			@comprehension  : '[' expression 'for' IDENT 'in' expression ( 'if' expression )? ']'
							;

			@evaluation     : expression ;

			expression      : test ;

			@test   	    : if_else
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

			power		    : @(atom "**" factor)
							| atom
							;

			atom		    : ( "True" | "False" )
							| call
							| NUMBER
							| @path(path_list)
							| strings
							| comprehension
							| list
							| @( '(' expression ')' )
							;

			path_list       : path_list '.' IDENT
							| IDENT
							;

			@call           : IDENT '(' ( test (',' test )* )? ')';
			@list           : '[' ( test (',' test )* )? ']' ;
			@strings        : STRING+ ;
			""")

		self.functions = {}
		self.functions["upper"] = Function(lambda x: str.upper(x),
		                                                "return String(arguments[0]).toUpperCase();")
		self.functions["lower"] = Function(lambda x: str.lower(x),
		                                                "return String(arguments[0]).toLowerCase();")
		self.functions["str"] = Function(lambda x: str(x),
		                                                "return String(arguments[0]);")
		self.functions["int"] = Function(lambda x: int(x),
		                                                "return parseInt(arguments[0]);")
		self.functions["float"] = Function(lambda x: float(x),
		                                                "return parseFloat(arguments[0]);")
		self.functions["len"] = Function(lambda x: len(x), "return arguments[0].length;")


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
		self.evaluate = False
		self.stack = []
		self.fields = {}

	def getOperands(self, onlyNumeric = True):
		r = self.stack.pop()
		l = self.stack.pop()

		if isinstance(l, str) or isinstance(r, str):
			if onlyNumeric:
				try:
					l = float(l)
				except:
					l = 0

				try:
					r = float(r)
				except:
					r = 0
			else:
				l = self.optValue(l)
				r = self.optValue(r)

		return l, r

	def optValue(self, val):
		if isinstance(val, list) and len(val) == 1:
			val = val[0]

		if isinstance(val, str):
			v = self.parseInt(val, None)
			if v is not None:
				return v

			v = self.parseFloat(val, None)
			if v is not None:
				return v
		elif any([isinstance(val, t) for t in [int, bool, float]]):
			return val

		return str(val)

	def parseInt(self, s, ret = 0):
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

	def parseFloat(self, s, ret = 0.0):
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

	def execute(self, src, fields = None, dump = False):
		if self.stack:
			self.stack = []

		if isinstance(fields, dict):
			self.fields = fields

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


	# Traversal functions

	def pre_evaluation(self, node):
		self.evaluate = True

	def post_evaluation(self, node):
		self.evaluate = False

	def pre_comprehension(self, node):
		self.evaluate = False

	def post_comprehension(self, node):
		#print("COMPREHENSION")
		#print(self.stack)
		#self.dump(node.children[2])

		self.evaluate = True
		iter = self.execute(node.children[2], self.fields)

		ret = []
		tfields = self.fields.copy()

		for var in iter:
			tfields[node.children[1].match] = var

			if len(node.children) == 4 and not self.execute(node.children[3], tfields):
				continue

			ret.append(self.execute(node.children[0], tfields))

		self.stack.append(ret)

	# Evaluational-depending traversal functions

	def post_or_test(self, node):
		if not self.evaluate:
			return

		for i in range(1, len(node.children)):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append(l or r)

	def post_and_test(self, node):
		if not self.evaluate:
			return

		for i in range(1, len(node.children)):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append(l and r)

	def post_not_test(self, node):
		if not self.evaluate:
			return

		self.stack.append(not self.stack.pop())

	def post_comparison(self, node):
		if not self.evaluate:
			return

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
		if not self.evaluate:
			return

		l, r = self.getOperands(False)

		if isinstance(l, str) or isinstance(r, str):
			if not isinstance(l, str):
				l = str(l)
			else:
				r = str(r)

		#print("add", type(l), l, type(r), r)
		self.stack.append(l + r)

	def post_sub(self, node):
		if not self.evaluate:
			return

		l, r = self.getOperands()

		#print("sub", type(l), l, type(r), r)
		self.stack.append(l - r)

	def post_mul(self, node):
		if not self.evaluate:
			return

		l, r = self.getOperands(False)

		if isinstance(l, str) and isinstance(r, str):
			r = 0
		elif isinstance(l, str) or isinstance(r, str):
			if self.parseInt(l, None) is not None:
				l = int(l)
			elif self.parseInt(r, None) is not None:
				r = int(r)

		#print("mul", type(l), l, type(r), r)
		self.stack.append(l * r)

	def post_div(self, node):
		if not self.evaluate:
			return

		l, r = self.getOperands()

		#print("div", type(l), l, type(r), r)
		self.stack.append(l / r)

	def post_mod(self, node):
		if not self.evaluate:
			return

		l, r = self.getOperands()

		#print("mod", type(l), l, type(r), r)
		self.stack.append(l % r)

	def post_factor(self, node):
		if not self.evaluate:
			return

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

	def post_path(self, node):
		if not self.evaluate:
			return

		field = self.fields

		for part in node.children:
			#print(part.match, field)

			if not isinstance(field, dict):
				field = "<invalid data path @ '%s'>" % ".".join([_.match for _ in node.children])
				break

			field = field.get(part.match, "")

		self.stack.append(self.optValue(field))

	def post_True(self, node):
		if not self.evaluate:
			return

		self.stack.append(True)

	def post_False(self, node):
		if not self.evaluate:
			return

		self.stack.append(False)

	def post_call(self, node):
		if not self.evaluate:
			return

		func = node.children[0].match

		l = []
		for i in range(1, len(node.children)):
			l.append(self.stack.pop())

		if not func in self.functions.keys():
			return

		self.stack.append(self.functions[func].call(*reversed(l)))

	def post_STRING(self, node):
		if not self.evaluate:
			return

		self.stack.append(node.match[1:-1])

	def post_strings(self, node):
		if not self.evaluate:
			return

		s = ""
		for i in range(len(node.children)):
			s = str(self.stack.pop()) + s

		self.stack.append(s)

	def post_list(self, node):
		if not self.evaluate:
			return

		l = []
		for i in range(0, len(node.children)):
			l.append(self.stack.pop())

		l.reverse()

		self.stack.append(l)

	def post_NUMBER(self, node):
		if not self.evaluate:
			return

		if "." in node.match:
			self.stack.append(self.parseFloat(node.match))
		else:
			self.stack.append(self.parseInt(node.match))

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
