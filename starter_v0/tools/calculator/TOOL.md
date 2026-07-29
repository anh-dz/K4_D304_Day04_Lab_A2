---
name: calculator
track: core
kind: local_formatter
provider: Python standard library
requires_env: []
inputs: [expression]
outputs: [expression, result, error]
side_effect: false
---
# calculator

Safely evaluates a finite numeric expression locally. It never evaluates Python
code, imports modules, reads files, or accesses the network.

Use it for arithmetic with known numeric inputs, percentages converted to a
decimal expression, and approved functions/constants from Python's `math`
namespace. Examples:

- `0.15 * 25000`
- `math.sqrt(144)`
- `math.pi * 5**2`
- `sin(pi / 4)`

Do not use it for symbolic algebra, indefinite integrals, proofs, equation
solving, programming requests, or expressions with missing numeric inputs.

## Argument

- `expression`: a numeric expression using `+`, `-`, `*`, `/`, `//`, `%`, `**`,
  parentheses, approved math functions, and the constants `pi`, `e`, and `tau`.
