# ViUR logics & vistache

**logics** is a domain-specific, embeddable expressional language with a Python-style syntax.

**vistache** is a Mustache-style template engine powered by logics expressions.

## About

The initial intention behind logics was to serve a well-known syntax for expressing validity checks across all ViUR modules and execution platforms. Starting from the administration tools to server-side input checking as well as client-side input forms. Therefore, logics code is only specified once at a particular place, and can be executed in pure Python (also compiled with PyJS) or compiled into native JavaScript.

But logics is not intended to be a scripting language! Therefore it neither provides direct variable assignment, nor control structures like loops or jumps - except comprehensions.

Moreover, it is a language and tool for...

- ...expressing validity checks,
- ...performing custom calculations,
- ...providing customizable templating features,
- ...making data-driven decisions in a restricted and secure context.

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

## Building

The logics parser is implemented using the [UniCC](https://github.com/phorward/unicc) parser generator and its newly established Python support. Install UniCC as instructed. Then, run ``make`` to build the logics parser.

## Examples

Literals

```python
"Hello World"
2016
23.5
True
[1,2,3]
```

Simple arithmetic expressions

```python
23 / 5 + (1337 - 42)
```

Concatenate current content of a field (variable) with a string literal

```python
myfield + " is my value!"
```

Add enforced string content lengths of two fields firstname and lastname
and test them for a total length greater than 32 characters

```python
len(str(firstname)) + len(str(lastname)) > 32
```

Check if current content of field (variable) named `degree` is filled,
and `mother` or `father`, or current integer value of field `age` is
greater-equal 21 and lower-equal 42.

```python
(degree and degree in ["mother", "father"]) or (int(age) >= 21 and int(age) <= 42)
```

Comprehensions are supported as well

```python
sum([x for x in [10, 52, 18.4, 99, 874, 13, 86] if x > 25]) # Sum all values higher 25
```

### Logics-based dependency checks in ViUR

The latest versions of [ViUR vi](https://github.com/viur-framework/vi) supports logics to dynamically change input mask behavior depending on input data.

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

## Vistache, the template engine

![Vistache Editor](https://lh3.googleusercontent.com/ygyA0TcqcR9id4MxzscYOqP0U49pHmKGnwvpwJ_iVdP6_LRRPkZK9KU5Ig5sSbeHm6zpe6Z6KkmUIp3zW7VI=s1024)

Vistache is an extension built on top of logics, allowing for a Mustache-like template language and engine. Likewise the original [Mustache](https://mustache.github.io/), a template is first compiled into an executable representation, then it can be rendered with variable data.

Instead of just outputting variables and performing conditional or iterative blocks, Vistage allows full logics expressions as shown in the example below.

Vistache expressions:

- `{{expression}}` outputs the result of expression
- `{{#expression}}...{{/}}` executes the block between the # and the / if expression validates to true. It also loops over the block when the expression results in a list, with a context-related sub-scoping.

```python
from logics.vistache import Template

x = Template("""Hello {{name}},

{{#persons}}{{name}} is {{age * 365}} days old{{#age > 33}}, and {{name * age}} is very old ;-){{/}}
{{/}}
Sincerely,

{{author}}""")

print(x.render({"name": "Bernd", "author": "Jan", "persons": [{"name": "John", "age": 33}, {"name": "Doreen", "age": 25}, {"name": "Valdi", "age": 39}]}))
```

## Contributing

We take a great interest in your opinion about ViUR. We appreciate your feedback and are looking forward to hear about your ideas. Share your visions or questions with us and participate in ongoing discussions.

- [ViUR website](https://www.viur.is)
- [ViUR on GitHub](https://github.com/viur-framework)
- [ViUR on Twitter](https://twitter.com/weloveViUR)

## Credits

ViUR is developed and maintained by [Mausbrand Informationssysteme GmbH](https://www.mausbrand.de/en), from Dortmund in Germany. We are a software company consisting of young, enthusiastic software developers, designers and social media experts, working on exciting projects for different kinds of customers. All of our newer projects are implemented with ViUR, from tiny web-pages to huge company intranets with hundreds of users.

Help of any kind to extend and improve or enhance this project in any kind or way is always appreciated.

## License

Copyright (C) 2012-2018 by Mausbrand Informationssysteme GmbH.

Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

You may use, modify and distribute this software under the terms and conditions of the GNU Lesser General Public License (LGPL). See the file LICENSE provided within this package for more information.
