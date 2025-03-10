<div align="center">
    <img src="https://github.com/viur-framework/viur-artwork/raw/main/icons/icon-logics.svg" height="196" alt="A hexagonal logo of Logics" title="Logics logo">
    <h1>Logics</h1>
    <a href="https://github.com/viur-framework/logics/actions/workflows/test.yml">
        <img src="https://github.com/viur-framework/logics/actions/workflows/test.yml/badge.svg" alt="Badge displaying the test status" title="Test badge">
    </a>
    <a href="https://github.com/viur-framework/logics/LICENSE">
        <img src="https://img.shields.io/github/license/viur-framework/logics" alt="Badge displaying the license" title="License badge">
    </a>
    <a href="https://pypi.org/project/logics-py">
        <img alt="Badge showing current PyPI version of logics-py" title="logics-py" src="https://img.shields.io/pypi/v/logics-py?label=logics-py">
    </a>
    <a href="https://www.npmjs.com/package/logics-js">
        <img alt="Badge showing current npm version of logics-js" title="logics-js" src="https://img.shields.io/npm/v/logics-js?label=logics-js">
    </a>
    <br>
    A multi-platform, sandboxed and extendable expression language with a Python-like syntax.
</div>

## About

Logics is a formula language with the aim of flexibly implementing programmable logics such as conditions, calculations or validations, so that developers as well as administrators and experienced users can use such expressions within a framework specified by the system to influence, calculate or otherwise dynamically adapt certain processes of a system.

The language can be compared to [Excel's formula language](https://github.com/microsoft/power-fx), where expressions can be defined based on variables and calculated dynamically. But Logics has a Python-like syntax at this point, but provides its own semantics, so that numbers and strings, for example, can be directly linked, None-values are assumed as 0, and Exceptions are generally not raised during execution.

In addition, Logics provides a sandbox environment, which does not allow potential attackers to break out of the provided environment or slow down the system. There are appropriate security mechanisms integrated into the language for this purpose.

Logics has been developed at [Mausbrand Informationssysteme GmbH](https://www.mausbrand.de/en) as part of the [ViUR ecosystem](https://www.viur.dev/), but it is a standalone project that can also be used outside the ViUR context.

Previous uses of Logics included

- event-based state evaluation
- dynamic rule systems
- programmable conditions for filters
- template engine generating text modules
- questionnaires with queries that depend on previous answers

## Usage

Since Logics is used on both the client and server side, the language was made available in two separate implementations.

- [logics-js](https://www.npmjs.com/package/logics-js) is a pure (vanilla) JavaScript implementation of Logics provided as npm-package.
- [logics-py](https://pypi.org/project/logics-py/) is a pure Python >= 3.10 implementation of Logics provided as PyPI-package.

Both packages are stand-alone without any further dependencies. They are both under recent development and stable until a specific degree right now. They are maintained in separate version numbers, which is planned to be changed soon, when they become almost feature-complete.

Using Logics in JavaScript:

```javascript
// npm install logics-js
import Logics from "logics-js";

let logics = new Logics("a + 2 * 3 + b");
console.log(logics.run({a: 1, b: "-Logics"}).toString()); // "7-Logics"
```

Using Logics in Python:
```python
# pip install logics-py
from logics import Logics

logics = Logics("a + 2 * 3 + b")
print(logics.run({"a": 1, "b": "-Logics"}))  # "7-Logics"
```

## Features

- Secure, native, running in a sandboxed environment apart from the host language
  - Disallows variable assignment, except in comprehensions
  - *logics-js*: Implementation in JavaScript
  - *logics-py*: Implementation in Python
- Python-inspired syntax and semantics
  - Make use of all standard operators
    - Unary `+`, `-`, `~`, `not`
    - Binary `+`, `*`, `-`, `/`, `//`, `**`
    - Comparison `==`, `!=`, `<>`, `<`, `<=`, `>`, `>=`, `in`, `not in`
    - Logical `and`, `or`
    - Conditions `y if x else z`
    - Comprehensions `[x for x in y if z]`
  - Slices `x[:]`
  - Attribute access `x[y]`
  - `# comments` in separate lines
  - Dedicated Value object abstraction of native types for
    - `None`
    - `True`, `False`
    - `int`, `float`, `str`
    - `list` for lists (similar to arrays)
    - `dict` for dicts (similar to structured objects)
- Provides a set of functions that can be used in expressions
- Extendable to custom functions
- Embeddable into other languages

## `Logics` vs. `Python`

Logics does look like Python, but it isn't Python!

It differs both in syntax and semantics:

- Expressions can be used with arbitrary whitespace and line-breaks
- There are no methods on objects, but functions that work on values, e.g.
  - Python's `dict.keys()` is `keys(dict)` in Logics
  - Python's `";".join(["a", "b", "c"])` is `join(["a", "b", "c"], ";")` in Logics
- No exceptions during runtime, but a defined behavior
  - Access to e.g. invalid index or key just returns `None`
  - Access of undefined variables returns `None`
  - Division by zero returns string `"#ERR: Division by zero"`
- Dynamic and automatic value conversion
  - e.g. the content of strings is automatically converted when used in calculations,
    so `"42" ** 3` produces 74088, and not a TypeError.

## Building & Packaging

Logics is built using the [UniCC LALR(1) Parser Generator](https://github.com/phorward/unicc), which supports generating parsers in multiple target languages. UniCC should be compiled from source, as the latest version 1.9+ is required.

Whenever something is changed on the syntax, ensure `unicc` is installed properly and run `make`, which regenerates the parser modules.

### Shared test cases

Logics-related test cases are placed as `*.lgx`-files into the `tests/` folder. They are shared by both implementations.

```logics
# In lgx-files, variables can be set using `#set:` as shown below.
# The part behind the second colon may contain any logics expression, including variables.
#set:x:6 * 7

#
# To verify if an expression produces an expected result, provide the expression followed by an `#expect:`.
#

x
#expect:42

x * x
#expect:1764
```

### logics-js

#### Formatting

To format the source code, use [prettier](https://www.npmjs.com/package/prettier) as follows:

```bash
cd logics-js
npm run fmt
```

#### Tests

Tests are implemented using [Mocha](https://mochajs.org/):

```bash
cd logics-js
npm test
```

#### Packaging

Publish on [npmjs.com](https://www.npmjs.com/):

```bash
cd logics-js
npm publish
```

### logics-py

#### Formatting

To format the source code, use [Black](https://github.com/psf/black) as follows:

```bash
cd logics-py
pipenv run fmt
```

#### Tests

Tests are implemented using [pytest](https://pytest.org):

```bash
cd logics-py
pipenv run test
```

#### Packaging

Publish on [PyPI](https://pypi.org/):

```bash
cd logics-py
pipenv install --dev
pipenv run build
pipenv run publish
pipenv run clean
pipenv --rm
```

## License

Copyright © 2025 by Mausbrand Informationssysteme GmbH.<br>
Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

Logics is free software under the MIT license.<br>
Please see the LICENSE file for details.
