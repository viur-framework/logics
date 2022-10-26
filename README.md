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

Logics is a tiny formula language, with the goal to provide equal syntax and semantics for different runtime contexts.

- [logics-js](https://www.npmjs.com/package/logics-js) is a pure JavaScript implementation of Logics provided as npm-package.
- [logics-py](https://pypi.org/project/logics-py/) is a pure Python implementation of Logics provided as PyPI-package.

Both packages are under recent development and not stable right now. They are maintained in separate version numbers.

## Features

- Python-like expression syntax, including list comprehensions
- Python-inspired type system for all JSON-serializable types
- Some Logics-specific specialities
- Separate implementations in JavaScript and Python with equal syntax and similar semantics
- Secure, running in a sandboxed environment apart from the host language
- Provides a set of functions to be used in expressions
- Extendable to custom functions

## License

Copyright © 2022 by Jan Max Meyer, Mausbrand Informationssysteme GmbH.<br>
Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

Logics is free software under the MIT license.<br>
Please see the LICENSE file for details.
