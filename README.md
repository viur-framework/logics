This software is a part of the ViUR® Information System.
ViUR® is a free software development framework for the Google App Engine™.
More about ViUR can be found at http://www.viur.is/.

DESCRIPTION
===========
*logics* is the attempt of implementing a domain-specific, Python-style
expressional language that can be compiled and executed in any of ViURs runtime
contexts.

The idea behind this project is to serve a well-known syntax to express
validity checks across all ViUR modules, from the administration tools to
server-side input checking as well as client-side input forms.

Therefore, *logics* code is only specified once at a particular place, and can
be executed in pure Python (also compiled with PyJS) or compiled to native
JavaScript.

It provides equal semantics and behavior for the same expressions on different
platforms.

**Warning:** *logics* is under heavy development and may change its API and/or
semantics.

FEATURES
========
- Provides the classes `logics.Parser` as the parser, `logics.Interpreter` as
  the interpreter, and `logics.JSCompiler` as the JavaScript compiler
- Logical operators `=`, `!=`, `<=`, `>=`, `in`, `not`, `not in`
- Inline `<expression> if <condition> else <expression>`
- Basic arithmetics `+`, `-`, `*`, `/`
- Data types `bool`, `int`, `float`, `str`, `[list]`
- Some dynamically extendible build-in functions, like
  `upper()`, `lower()`, `str()`, `int()`, `float()`, `len()`

USAGE
=====
*logics.py* can be used as a command-line tool for invocation and testing.

	usage: logics.py [-h] [-D] [-e] [-v var value] [-r] [-j] [-J] [-V] expression
	
	ViUR Logics Expressional Language
	
	positional arguments:
	  expression            The expression to compile
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -D, --debug           Print debug output
	  -e, --environment     Import environment as variables
	  -v var value, --var var value
	                        Assign variables
	  -r, --run             Run expression using interpreter
	  -j, --javascript      Compile expression to JavaScript
	  -J, --javascript+api  Compile expression to JavaScript with API
	  -V, --version         show program's version number and exit

DEPENDENCIES
============
*logics* is implemented using the pynetree Parsing Library, http://pynetree.org.

pynetree is free software under the MIT license, and is included in this
repository.

EXAMPLES
========
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

USING LOGICS IN VI
------------------
viur/vi currently supports within the branch *viurDepends* a support for
*logics* expressions to dynamically change input mask behavior depending
on input data.

The logics expressions are triggered on an event base, when input field contents
are changed.

The following events are supported so far:

- `logic.visibleIf` sets the field visible when the expression returns `True`
- `logic.readonlyIf` sets the field read-only when the expression returns `True`
- `logic.evaluate` sets the field's value according to the provided expression

The expressions are provided by extending skeleton bones to specific expressions
on the particular event.

	class fieldSkel(Skeleton):
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

LICENSING
=========
Copyright (C) 2016, 2017 by Mausbrand Informationssysteme GmbH.

Mausbrand and ViUR are registered trademarks of
Mausbrand Informationssysteme GmbH.

You may use, modify and distribute this software under the terms and
conditions of the GNU Lesser General Public License (LGPL).

See the file LICENSE provided in this package for more information.

WHO DO I TALK TO?
=================
For problems, questions and enhancement request, contact @codepilot.
