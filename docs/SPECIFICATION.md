# Global Value Expansion Model

## Overview

OKW defines a unified value expansion mechanism for all Robot Framework
libraries within the OKW ecosystem.

The placeholder syntax:

    $MEM{KEY}

is used to reference values stored in the Memorized Value Store.

This mechanism is implemented in the shared utility library
`okw-contract-utils` and MUST be used consistently across all
`robotframework-okw-*` libraries.

---

## Placeholder Syntax

### $MEM{KEY}

- KEY is case-sensitive
- Allowed characters: A-Z, a-z, 0-9, `_`, `-`, `.`
- Multiple placeholders may appear in a single string
- Placeholders may appear anywhere inside a string

Example:

    Set Value    ${status}    Result is $MEM{BUILD_ID}

---

## Resolution Rules

1. Expansion MUST occur before:
   - execution of actions (`Set ...`)
   - verification (`Verify ...`)
   - forwarding values to adapters
2. Expansion applies to parameters classified as:
   - Value
   - Command
3. Expansion MUST be deterministic.
4. Missing KEY MUST cause immediate failure.
5. Expansion MUST NOT silently ignore missing keys.
6. Expansion MUST NOT modify non-value parameters.

---

## Failure Behavior

If a placeholder references a non-existing key:

    $MEM{UNKNOWN_KEY}

the keyword MUST fail with a configuration error.

Silent fallback or partial substitution is not permitted.

---

## Scope

The Memorized Value Store:

- is library-scoped unless explicitly documented otherwise
- may be session-scoped in adapter libraries
- must behave deterministically

---

## Architectural Rationale

This mechanism ensures:

- Cross-adapter consistency
- Deterministic value resolution
- ASR-model compatibility
- Elimination of hidden state dependencies
- Uniform AI-generatable test semantics
