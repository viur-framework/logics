# DESCRIPTION #

*logics* is an attempt of providing a Python-style expressional language with
an integrated interpreter and a compiler generating JavaScript code as its
output.

The idea behind this project is to serve a well-known syntax to express validity
checks across all ViUR-modules, from the administration tools to server-side
input checking as well as client-side input forms. So *logics* code is only
specified once at a particular place, and can be executed in pure Python (also
compiles with pyJS) or compiled to native JavaScript.

It provides equal semantics and behavior for the same expressions on different
platforms.

# FEATURES #

- Provides the classes `logics.viurLogicsParser` as the parser,
  `logics.viurLogicsExecutor` as the interpreter, and
  `logics.viurLogicsJS` as the JavaScript compiler
- Logical operators `=`, `!=`, `<=`, `>=`, `in`, `not`, `not in`
- Inline `<expression> if <condition> else <expression>`
- Basic arithmetics `+`, `-`, `*`, `/`
- Data types `bool`, `int`, `float`, `str`, `[list]`
- Some dynamically extendable build-in functions, like
  `upper()`, `lower()`, `str()`, `int()`, `float()`, `len()`

# EXAMPLES #

Literals

	"Hello World"
	2016
	23.5
	True
	[1,2,3]

Arithmetic expressions

	23 / 5 + (1337 - 42)

Concatenate current content of a field (variable) with a string literal

	myfield + " is my value!"

Add enforced string content lengths of two fields firstname and lastname
and test them for a total length greater than 32 characters

	len(str(firstname)) + len(str(lastname)) > 32

Check if current content of field (variable) named `degree` is filled,
and `mother` or `father`, or current integer value of field `age` is
greater-equal 21 and lower-equal 42.

	(degree and degree in ["mother", "father"])
		or (int(age) >= 21 and int(age) <= 42)

## LOGICS IN VIUR VI ##

viur/vi currently supports within the branch *viurDepends* a support of
*logics* expressions, to dynamically change input mask behavior depending
on input data.

The logics expressions are executed event-based, when input field contents
are changed. The following events are supported so far:

- `logic.visibleIf` sets the field visible when the expression returns `True`
- `logic.readonlyIf` sets the field read-only when the expression returns `True`

The expressions are provided by extending skeleton bones to specific expressions
on the particular event.

	type = selectOneBone(descr="Type",
							values={
								"level":u"Leveling",
		                        "bool":u"Boolean",
		                        "text":u"Text (single line)",
		                        "memo":u"Text (multi-line)",
		                        "select":u"Selection field",
		                        "table":u"Table",
		                        "query": u"Output field"},
	                        required=True, defaultValue="level")
	value = stringBone(descr="Default value",
						params={"logic.visibleIf": 'type != "level"'})
	entries = stringBone(descr="Possible values",
							params={"logic.visibleIf": 'type == "select"'},
							multiple=True)
	required = booleanBone(descr="Required",
							params={"logic.visibleIf":
										'type in ["text", "memo"]'},
							defaultValue=False)
	multiple = booleanBone(descr="Multiple entries",
							params={"logic.visibleIf":
										'type in ["text", "memo", "select"]'},
							defaultValue=False)
	columns = stringBone(descr="Columns",
							multiple=True,
							params={"visibleIf": 'type == "table"'})

# USAGE #

Getting a raw parser

	from logics import viurLogicsParser

	vil = viurLogicsParser()
	vil.dump(vil.compile("a in b(13)"))

Getting an executor and run an expression

	from logics import viurLogicsExecutor

	vile = viurLogicsExecutor()
	print(vile.execute("float(upper('23.4')) + 1"))

Getting an running a JavaScript compiler

	from logics import viurLogicsJS

	viljs = viurLogicsJS()
	print(viljs.api())
	print(viljs.compile('type in ["text", "memo"] and required == "1"'))

More to come later on! :-)