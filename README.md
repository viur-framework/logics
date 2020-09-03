# ViUR logics / ViUR vistache

**logics** is a domain-specific, embeddable expressional language with a Python-style syntax.
**vistache** provides a customizable template language and engine powered by logics expressions.

## About

The initial intention behind logics was to serve a well-known syntax for expressing validity checks across all ViUR modules and its execution platforms. This starts from the administration tools to server-side input checking as well as client-side input forms and user-defined template processing.

The first version of logics was intended to allow both direct expression execution and expression compilation into native JavaScript code, to be executed on the client without the need of a logics interpreter. This feature has been disabled for now, but may be re-implemented in the future when needed.

logics is __not__ intended to be a scripting language! Therefore it neither provides direct variable assignment, nor control structures like loops or jumps - except for comprehensions.

Rather than that, it is a language and tool for...

- ...expressing validity checks,
- ...performing custom calculations,
- ...providing customizable templating features,
- ...making data-driven decisions in a restricted and secure runtime context.

## Usage

*logics.py* can be used as a command-line tool for invocation and testing.

```
usage: logics.py [-h] [-D] [-e] [-v var value] [-r] [-V] expression

ViUR Logics Expressional Language

positional arguments:
  expression            The expression to be processed

optional arguments:
  -h, --help            show this help message and exit
  -D, --debug           Print debug output
  -e, --environment     Import environment as variables
  -v var value, --var var value
                        Assign variables
  -r, --run             Run expression using interpreter
  -V, --version         show program's version number and exit
```

## Building

The logics parser is implemented using the [UniCC](https://github.com/phorward/unicc) parser generator and its newly established Python support. Install UniCC as instructed in its README, or download a setup for your platform. Then, run `make` to build the logics parser.

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

The latest versions of [ViUR vi](https://github.com/viur-framework/vi) support logics to dynamically change input mask behavior depending on input data.

The logics expressions are triggered on an event base, when input field contents are changed.

The following events are supported so far:

- `logic.visibleIf` sets the field visible when the expression returns `True`
- `logic.readonlyIf` sets the field read-only when the expression returns `True`
- `logic.evaluate` sets the field's value according to the provided expression

The expressions are provided by extending skeleton bones to specific expressions on the particular event.

```python
class fieldSkel(Skeleton):
    type = selectBone(
        descr="Type",
        values={
            "none": u"None",
            "text": u"Text (single line)",
            "memo": u"Text (multi-line)",
            "select": u"Selection field"
        },
        required=True, defaultValue="level"
    )
    value = stringBone(
        descr="Default value",
        params={"logic.visibleIf": 'type != "none"'}
    )
    entries = stringBone(
        descr="Possible values",
        params={"logic.visibleIf": 'type == "select"'},
        multiple=True
    )
    required = booleanBone(
        descr="Required",
        params={"logic.visibleIf": 'type in ["text", "memo"]'},
        defaultValue=False
    )
    multiple = booleanBone(
        descr="Multiple entries",
        params={"logic.visibleIf": 'type in ["text", "memo", "select"]'},
        defaultValue=False
    )
```

---

## Vistache: A logics-powered template language

![Vistache used in a template editor](https://lh3.googleusercontent.com/ygyA0TcqcR9id4MxzscYOqP0U49pHmKGnwvpwJ_iVdP6_LRRPkZK9KU5Ig5sSbeHm6zpe6Z6KkmUIp3zW7VI=s1024)

Vistache is built on top of logics, providing an easy-to-use template language with a [Mustache](https://mustache.github.io/)-inspired syntax. Similar to the original Mustache, a template is first compiled into an executable representation, then it can be rendered with variable data.

Instead of just outputting variables and performing conditional or iterative blocks, Vistache allows to use full logics expressions as shown in the example below.

Vistache expressions:

- `{{expression}}` just renders the result of expression
- `{{#expression}}...{{/}}` renders the block between `{{#expression}}` and the `{{/}}` if the expression validates to true. It also loops over the block when the expression results in a list, with a context-related sub-scoping.
- `{{#expression}}...{{|}}...{{/}}` renders the block between the `{{#expression}}` and the `{{|}}` if the expression validates to true, otherwise it renders the block between the `{{|}}` and `{{/}}`. It also loops over the first block when the expression results in a list, with a context-related sub-scoping.
- `{{#expression}}...{{|other-expression1}}...{{|other-expression2}}...{{|}}...{{/}}` a variant of an if-elseif-elseif-else-construct.

In case of a loop in the conditional blocks above, a variable `loop` is also made available in each scope, containing the following members:

- `loop.length` is the number of items that are looped,
- `loop.item` is the full context-based variable,
- `loop.index` is the loop conter starting at 1,
- `loop.index0` is the loop conter starting at 0,
- `loop.first` is true on the first loop,
- `loop.last` is true on the last loop.
- `loop.parent` points to the previous loop block variable (None on outer loop)

This feature is inspired by the Jinja2 template engine.

Running the template

```vistache
{{#persons}}Hello {{firstname}}
	{{#city}} from {{city}}{{/}}!

	{{# dogs and len(dogs) }}
		You have {{len(dogs)}} dog{{ "s" if len(dogs) > 1 else "" }} named
		{{#dogs}}
			{{#loop.last and not loop.first}} and
			{{/}}
			{{loop.item}}
			{{#loop.index < len(dogs) - 1}},
			{{/}}
		{{/}}
	{{|}}
		There is no dog living with you.
	{{/}}
{{/}}
```

with the JSON object

```json
[
	{
		"firstname": "John",
		"city": "Johannesburg"
	},
	{
		"firstname": "Bernd",
		"dogs": ["Doge"]
	},
	{
		"firstname": "Max",
		"city": "Dortmund",
		"dogs": ["Shugar", "Kira", "Akela"]
	}
]
```

results in the following output:

```
Hello John from Johannesburg!
        There is no dog living with you.
Hello Bernd!
        You have 1 dog named Doge
Hello Max from Dortmund!
        You have 3 dogs named Shugar, Kira and Akela
```

Try it out by calling

```bash
python vistache.py -v persons persons.json -r persons.vistache
```

from a command-line.

## Contributing

We take great interest in your opinion about ViUR. We appreciate your feedback and are looking forward to hear about your ideas. Share your vision or questions with us and participate in ongoing discussions.

- [ViUR website](https://www.viur.is)
- [#ViUR on freenode IRC](https://webchat.freenode.net/?channels=viur)
- [ViUR on GitHub](https://github.com/viur-framework)
- [ViUR on Twitter](https://twitter.com/weloveViUR)

## Credits

ViUR is developed and maintained by [Mausbrand Informationssysteme GmbH](https://www.mausbrand.de/en), from Dortmund in Germany. We are a software company consisting of young, enthusiastic software developers, designers and social media experts, working on exciting projects for different kinds of customers. All of our newer projects are implemented with ViUR, from tiny web-pages to huge company intranets with hundreds of users.

Help of any kind to extend and improve or enhance this project in any kind or way is always appreciated.

## License

Copyright (C) 2012-2020 by Mausbrand Informationssysteme GmbH.

Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

You may use, modify and distribute this software under the terms and conditions of the GNU Lesser General Public License (LGPL). See the file LICENSE provided within this package for more information.
