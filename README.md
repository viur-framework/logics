# logics

**logics** is an embeddable, expressional language with a Python-style syntax.

## About

The initial intention behind logics is to serve a well-known syntax for expressing validity checks across all ViUR modules, from the administration tools to server-side input checking as well as client-side input forms. Therefore, logics code is only specified once at a particular place, and can be executed in pure Python (also compiled with PyJS) or compiled into native JavaScript.

Newer developments are also using logics also as some kind of universal templating language.

But logics is not intended to be a scripting language! Therefore it neither provides variable assignment, nor control structures like loops or jumps. Moreover, it is a language to...

- ...express validity checks.
- ...perform template processing.
- ...provide a way to perform customized data processing.


**Warning:** This project is under heavy development and may change its API and/or semantics.

## Features

- Provides the classes `logics.Parser` as the plain parser,
  - `logics.Interpreter` as the interpreter,
  - and `logics.JSCompiler` as the JavaScript compiler
- Logical operators `=`, `!=`, `<=`, `>=`, `in`, `not`, `not in`
- Inline `<expression> if <condition> else <expression>`
- Basic arithmetics `+`, `-`, `*`, `/`
- Data types `bool`, `int`, `float`, `str`
- An array type `[list]`
- Some dynamically extendible build-in functions, like `upper()`, `lower()`, `str()`, `int()`, `float()`, `len()`

## Usage

*logics.py* can be used as a command-line tool for invocation and testing.

```
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
```

## Dependencies

logics is implemented using the UniCC Parser Generator, https://github.com/phorward/unicc.

## Examples

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

## Logics in ViUR Vi

[ViUR vi](https://github.com/viur-framework/vi) currently supports logics to dynamically change input mask behavior depending on input data.

The logics expressions are triggered on an event base, when input field contents are changed.

The following events are supported so far:

- `logic.visibleIf` sets the field visible when the expression returns `True`
- `logic.readonlyIf` sets the field read-only when the expression returns `True`
- `logic.evaluate` sets the field's value according to the provided expression

The expressions are provided by extending skeleton bones to specific expressions on the particular event.

```python
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
```

## Contributing

We take a great interest in your opinion about ViUR. We appreciate your feedback and are looking forward to hear about your ideas. Share your visions or questions with us and participate in ongoing discussions.

- [ViUR on the web](https://www.viur.is)
- [#ViUR on freenode IRC](https://webchat.freenode.net/?channels=viur)
- [ViUR on Google Community](https://plus.google.com/communities/102034046048891029088)
- [ViUR on Twitter](https://twitter.com/weloveViUR)

## Credits

ViUR is developed and maintained by [Mausbrand Informationssysteme GmbH](https://www.mausbrand.de/en), from Dortmund in Germany. We are a software company consisting of young, enthusiastic software developers, designers and social media experts, working on exciting projects for different kinds of customers. All of our newer projects are implemented with ViUR, from tiny web-pages to huge company intranets with hundreds of users.

Help of any kind to extend and improve or enhance this project in any kind or way is always appreciated.

## License

ViUR is Copyright (C) 2012-2018 by Mausbrand Informationssysteme GmbH.

Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

You may use, modify and distribute this software under the terms and conditions of the GNU Lesser General Public License (LGPL). See the file LICENSE provided within this package for more information.
