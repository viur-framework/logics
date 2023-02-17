<div align="center">
    <img src="https://github.com/viur-framework/viur-artwork/raw/main/icons/icon-logics.svg" height="196" alt="A hexagonal logo of Logics" title="Logics logo">
    <h1>Logics</h1>
    <a href="https://pypi.org/project/logics-py">
        <img alt="Badge showing current PyPI version if logics-py" title="logics-py" src="https://img.shields.io/pypi/v/logics-py?label=logics-py">
    </a>
    <a href="https://www.npmjs.com/package/logics-js">
        <img alt="Badge showing current npm version if logics-js" title="logics-js" src="https://img.shields.io/npm/v/logics-js?label=logics-js">
    </a>
    <a href="LICENSE">
        <img src="https://img.shields.io/github/license/viur-framework/logics" alt="Badge displaying the license" title="License badge">
    </a>
    <br>
    A tiny, sandboxed, secure and extendable formula language with a flavor of Python.
</div>

## About

Logics is a simple expression language with the goal to provide equal syntax and semantics for different runtime contexts and host languages.

- [logics-js](https://www.npmjs.com/package/logics-js) is a pure JavaScript implementation of Logics provided as npm-package.
- [logics-py](https://pypi.org/project/logics-py/) is a pure Python implementation of Logics provided as PyPI-package.

Both packages are under recent development and not stable right now. They are maintained in separate version numbers.

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
    - `True`, `False`, `None`
    - `int`, `float`, `str`
    - `list` for arrays
    - `dict` for structured objects
- Provides a set of functions that can be used in expressions
- Extendable to custom functions

## `Logics` vs. `Python`

Logics does look like Python, but it isn't Python!

- Expressions can be used with arbitrary whitespace and line-breaks
- There are no methods on objects, but functions that work on objects
  - e.g. `dict.keys()` becomes `keys(dict)`
  - `";".join(["a", "b", "c"])` becomes `join(["a", "b", "c"], ";")`
- No exceptions, access to e.g. invalid index or key just returns `None`
- Dynamic and automatic value conversion

## License

Copyright © 2023 by Mausbrand Informationssysteme GmbH.<br>
Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

Logics is free software under the MIT license.<br>
Please see the LICENSE file for details.
