# Change Log

This file documents any relevant changes done to logics.

## [2.4] Agung

This is the current development version.

- Feature: New functions `replace`, `rstrip`, `lstrip` and `strip`
- Feature: Vistache-function `htmlInsertImage` improved to flip-parameter.
- Bugfix: `logics.utility.strType` variable defines string type to use 
- Bugfix: Empty list traversal handled more faithfully
- Bugfix: Stability in `in` and `not in` tests

## [2.3] Kilauea

Release date: Oct 2, 2018

- Changed semantics for softer value optimization
- New function ``split()`` for logics
- New function ``formatCurrency()` for Vistache
- New {{|}} else block notation added to Vistache
- Improved Vistache loop variable processing
- Avoid overriding existing keys within Vistache {{#if}} blocks

## [2.2] Etna

(Previously referred as 0.7)
Release date: Apr 23, 2018

- Vistache Template Engine
- Improved semantics in interpreter
- Removed out-dated JavaScript compiler + API
- Entirely new parser implemented with [UniCC v1.3](https://github.com/phorward/unicc)
- New version numbering synchronized with ViUR
- CHANGELOG added

## [2.1]

(Previously referred as 0.6)
Release date: Nov 02, 2017

- Many bugfixes and improvements
- First version included in [ViUR vi](https://github.com/viur-framework/vi)
- Major improvements

## [0.5]

- Reworking the language and introducing the entity traversals, allowing
  for iterating and accessing indexes, keys or even functions

## [0.4]

- Iterative comprehensions
- Command-line interface
- LICENSE and README files

## 0.1 - 0.3

- Initial parser implemented using [pynetree](https://github.com/phorward/pynetree)
- Conditional and arithmetic expressions
- Demos implemented to run both in [ViUR vi](https://github.com/viur-framework/vi) and a native JavaScript frontend
- JavaScript API


[develop]: https://github.com/viur-framework/logics/compare/v2.3.0...develop
[2.4]: https://github.com/viur-framework/logics/compare/v2.3.0...develop
[2.3]: https://github.com/viur-framework/logics/compare/v2.2.0...v2.3.0
[2.2]: https://github.com/viur-framework/logics/compare/v2.1...v2.2.0
[2.1]: https://github.com/viur-framework/logics/compare/v0.5...v2.1
[0.5]: https://github.com/viur-framework/logics/compare/v0.4...v0.5
[0.4]: https://github.com/viur-framework/logics/compare/v0.3...v0.4
