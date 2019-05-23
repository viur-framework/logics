# Changelog

This file documents any relevant changes done to logics & vistache.

## [develop] 

This is the current development version.

## [2.4.1] Agung

Release date: May 24, 2019

- Bugfix: unary operators (+, -, ~) where incorrectly traversed

## [2.4.0] Agung

Release date: May 17, 2019

- Feature: New functions `replace()`, `rstrip()`, `lstrip()` and `strip()`
- Feature: Vistache-function `formatCurrency()` renamed to `currency()`, added support for currency char and moved into logics
- Feature: Vistache-function `htmlInsertImage` improved to flip-parameter for image flipping
- Bugfix: `logics.utility.strType` variable defines string type to use 
- Bugfix: More reliable empty list traversal
- Bugfix: More reliable `in` and `not in` operators

## [2.3.0] Kilauea

Release date: Oct 2, 2018

- Changed semantics for softer value optimization
- New function ``split()`` for logics
- New function ``formatCurrency()` for Vistache
- New {{|}} else block notation added to Vistache
- Improved Vistache loop variable processing
- Avoid overriding existing keys within Vistache {{#if}} blocks

## [2.2.0] Etna

(Previously referred as 0.7)
Release date: Apr 23, 2018

- Vistache Template Engine
- Improved semantics in interpreter
- Removed out-dated JavaScript compiler + API
- Entirely new parser implemented with [UniCC v1.3](https://github.com/phorward/unicc)
- New version numbering synchronized with ViUR
- CHANGELOG added

## [2.1.0]

(Previously referred as 0.6)
Release date: Nov 02, 2017

- Many bugfixes and improvements
- First version included in [ViUR vi](https://github.com/viur-framework/vi)
- Major improvements

## [0.5.0]

- Reworking the language and introducing the entity traversals, allowing
  for iterating and accessing indexes, keys or even functions

## [0.4.0]

- Iterative comprehensions
- Command-line interface
- LICENSE and README files

## 0.1 - 0.3

- Initial parser implemented using [pynetree](https://github.com/phorward/pynetree)
- Conditional and arithmetic expressions
- Demos implemented to run both in [ViUR vi](https://github.com/viur-framework/vi) and a native JavaScript frontend
- JavaScript API


[develop]: https://github.com/viur-framework/logics/compare/v2.4.0...develop
[2.4.0]: https://github.com/viur-framework/logics/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/viur-framework/logics/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/viur-framework/logics/compare/v2.1...v2.2.0
[2.1.0]: https://github.com/viur-framework/logics/compare/v0.5...v2.1
[0.5.0]: https://github.com/viur-framework/logics/compare/v0.4...v0.5
[0.4.0]: https://github.com/viur-framework/logics/compare/v0.3...v0.4
