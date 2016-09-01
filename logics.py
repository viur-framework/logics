#-*- coding: utf-8 -*-
"""
Implements the tiny dependency check language "viurLogic" that can be compiled
into JavaScript or directly executed within an interpreter. It is entirely
written in pure Python.
"""

from pynetree import Parser

class viurLogicsFunction(object):
	def __init__(self, call, js):
		if not callable(call):
			raise TypeError("Parameter must be callable")

		self.call = call

		if not isinstance(js, str):
			raise TypeError("Parameter must be str")

		self.js = js

class viurLogicsParser(Parser):

	functions = None

	def __init__(self):
		super(viurLogicsParser, self).__init__(
			"""
			$			/\\s+|#.*\n/											%skip;
			$NAME		/[A-Za-z_][A-Za-z0-9_]*/ 								%emit;
			$STRING 	/"[^"]*"|'[^']*'/ 										%emit;
			$NUMBER 	/[0-9]+\.[0-9]*|[0-9]*\.[0-9]+|[0-9]+/ 					%emit;

			test %goal	: if_else
						| or_test                            					%emit
						;

			if_else     : or_test 'if' or_test 'else' test   					%emit;

			or_test		: and_test ('or' and_test)+ 							%emit
						| and_test
						;

			and_test	: not_test ('and' not_test)+ 							%emit
						| not_test
						;

			not_test	: 'not' not_test 										%emit
						| comparison
						;
			comparison	: expr (( "==" | ">=" | "<=" | "<" | ">" |
									"<>" | "!=" | "in" | not_in) expr)+ 		%emit
						| expr
						;

			not_in		: 'not' 'in' 											%emit;

			expr		: add | sub | term;
			add			: expr '+' term 										%emit;
			sub			: expr '-' term 										%emit;

			term		: mul | div | mod | factor;
			mul			: term '*' factor										%emit;
			div			: term '/' factor										%emit;
			mod			: term '%' factor										%emit;

			factor		: ("+"|"-"|"~") factor									%emit
						| power
						;
			power		: atom "**" factor 										%emit
						| atom
						;

			atom		: call
						| NUMBER
						| field
						| strings
						| list
						| '(' test ')'                                          %emit
						;

			call        : NAME '(' ( test (',' test )* )? ')'                   %emit;
			field       : NAME                                                  %emit;
			list        : '[' ( test (',' test )* )? ']'                        %emit;
			strings		: STRING+												%emit;
			""")

		self.functions = {}
		self.functions["upper"] = viurLogicsFunction(lambda x: str.upper(x),
		                                                "return String(arguments[0]).toUpperCase();")
		self.functions["lower"] = viurLogicsFunction(lambda x: str.lower(x),
		                                                "return String(arguments[0]).toLowerCase();")
		self.functions["str"] = viurLogicsFunction(lambda x: str(x),
		                                                "return String(arguments[0]);")
		self.functions["int"] = viurLogicsFunction(lambda x: int(x),
		                                                "return parseInt(arguments[0]);")
		self.functions["float"] = viurLogicsFunction(lambda x: float(x),
		                                                "return parseFloat(arguments[0]);")
		self.functions["len"] = viurLogicsFunction(lambda x: len(x), "return arguments[0].length;")


	def compile(self, src):
		return self.parse(src)


class viurLogicsJS(viurLogicsParser):
	"""
	Compiler to emit viurLogics code as JavaScript code.
	"""
	stack = None

	def __init__(self):
		super(viurLogicsJS, self).__init__()
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
		for i in range(1, len(node.children), 2):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append("%s || %s" % (l, r))

	def post_and_test(self, node):
		for i in range(1, len(node.children), 2):
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
		func = node[1][0][1]

		l = []
		for i in range(1, len(node[1])):
			l.append(self.stack.pop())

		if not func in self.functions.keys():
			return

		l.reverse()
		self.stack.append("%s_%s(%s)" % (self.apiPrefix, func, ", ".join(l)))

	def post_field(self, node):
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
		self.stack.append(node[1])

class viurLogicsExecutor(viurLogicsParser):
	"""
	Interpreter class for the viurLogics.
	"""

	def __init__(self):
		super(viurLogicsExecutor, self).__init__()
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
				l = str(l)
				r = str(r)

		return l, r

	def execute(self, src, fields = None):
		if self.stack:
			self.stack = []

		if isinstance(fields, dict):
			self.fields = fields

		if isinstance(src, str):
			t = self.compile(src)
			if t is None:
				return None
		else:
			t = src

		self.traverse(t)
		return self.stack.pop()

	def post_or_test(self, node):
		for i in range(1, len(node.children), 2):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append(l or r)

	def post_and_test(self, node):
		for i in range(1, len(node.children), 2):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append(l and r)

	def post_not_test(self, node):
		self.stack.append(not self.stack.pop())

	def post_comparison(self, node):
		for i in range(1, len(node.children), 2):
			op = node.children[i].symbol
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
		self.stack.append(l + r)

	def post_sub(self, node):
		l, r = self.getOperands()
		self.stack.append(l - r)

	def post_mul(self, node):
		l, r = self.getOperands(False)
		if isinstance(l, str) and isinstance(r, str):
			l = 0

		self.stack.append(l * r)

	def post_div(self, node):
		l, r = self.getOperands()
		self.stack.append(l / r)

	def post_mod(self, node):
		l, r = self.getOperands()
		self.stack.append(l % r)

	def post_factor(self, node):
		op = self.stack.pop()

		if isinstance(op, (str, unicode)):
			self.stack.append(op)
		elif node[1][0][0] == "+":
			self.stack.append(+op)
		elif node[1][0][0] == "-":
			self.stack.append(-op)
		else:
			self.stack.append(~op)

	def post_field(self, node):
		name = node.children[0].match
		if name in ["True", "False"]:
			self.stack.append(True if name == "True" else False)
		else:
			self.stack.append(self.fields.get(name, ""))

	def post_call(self, node):
		func = node.children[0].match

		l = []
		for i in range(1, len(node.children)):
			l.append(self.stack.pop())

		if not func in self.functions.keys():
			return

		self.stack.append(self.functions[func].call(*reversed(l)))

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

		self.stack.append(l)

	def post_NUMBER(self, node):
		if "." in node.match:
			self.stack.append(float(node.match))
		else:
			self.stack.append(int(node.match))


if __name__ == "__main__":
	vil = viurLogicsParser()
	vil.dump(vil.compile("a in b(13)"))

	vile = viurLogicsExecutor()
	print(vile.execute("float(upper('23.4')) + 1"))

	viljs = viurLogicsJS()
	print(viljs.api())
	print(viljs.compile('type in ["text", "memo"] and required == "1"'))
