# xDSL: Sidekick Compilation for SSA-Based Compilers

**Summary by:** GPT 6 Astra

**Author:** Mathieu Fehr, Michel Weber, Christian Ulmann, Alexandre Lopoukhine, Martin Paul Lücke, Théo Degioanni, Christos Vasiladiotis, Michel Steuwer, Tobias Grosser

**Source:** CGO 2025, pages 179-192

**Link:** https://doi.org/10.1145/3696443.3708945

**Code and documentation:** [xDSL](https://github.com/xdslproject/xdsl), [documentation](https://docs.xdsl.dev/), [paper artifact](https://doi.org/10.5281/zenodo.14263271)

## Key insight

Compiler frameworks can share programs and dialect definitions without sharing their implementation language or in-memory objects. xDSL uses that separation to support Python-native development while exchanging IR with MLIR's production-oriented C++ infrastructure.

## Basic idea

xDSL is a standalone Python compiler framework designed as a sidekick [1] to MLIR, not a Python binding to MLIR's implementation. Both use SSA operations, blocks, and regions [2], and exchange programs through a compatible textual representation [3]. Dialects can be defined with Python's PyRDL interface [4] and exchanged as declarative IRDL definitions [5]. Developers can therefore place Python transformations at selected points in a multi-level compilation pipeline [6], while keeping the remaining passes in MLIR; shared structure does not automatically share transformation code or prove semantic correctness [7].

## Illustrative example

**Define the operation.** Our `tiny.add` operation takes two 32-bit integers and returns their sum modulo `2^32`, without side effects. The following definition uses the xDSL 0.73.0 Python API:

```python
from xdsl.dialects.builtin import i32
from xdsl.ir import Dialect
from xdsl.irdl import (
    IRDLOperation,
    irdl_op_definition,
    operand_def,
    result_def,
)

@irdl_op_definition
class TinyAdd(IRDLOperation):
    name = "tiny.add"
    lhs = operand_def(i32)
    rhs = operand_def(i32)
    out = result_def(i32)

Tiny = Dialect("tiny", [TinyAdd])
```

PyRDL derives operand accessors and structural verification from this definition. It requires exactly two `i32` operands and one `i32` result. The Python class does not implement addition's meaning: that contract is our dialect's definition, and the lowering must respect it.

**Represent a program.** After registering `Tiny` and the standard `builtin` and `func` dialects, xDSL can parse this program:

```mlir
builtin.module {
  func.func @combine(%first: i32, %second: i32) -> i32 {
    %sum = "tiny.add"(%first, %second) : (i32, i32) -> i32
    func.return %sum : i32
  }
}
```

The function body is a region containing a block. Its arguments define `%first` and `%second`; `tiny.add` defines `%sum`, which the return uses. Quoting the operation name selects the generic operation syntax, avoiding a custom parser just for `tiny.add`.

**Share the schema.** The operand and result constraints are declarative, so they can be represented in the IRDL dialect and imported by either framework. Registering the equivalent schema in MLIR lets MLIR parse and structurally verify the custom operation. It does not tell MLIR how to optimize or execute it.

**Lower in Python.** Replace each `tiny.add` with the standard integer-add operation and redirect its uses:

```python
from xdsl.dialects import arith
from xdsl.rewriter import Rewriter

def lower_tiny(module):
    for op in list(module.walk()):
        if isinstance(op, TinyAdd):
            replacement = arith.AddiOp(op.lhs, op.rhs)
            Rewriter.replace_op(op, replacement)
```

The function's return uses the replacement result after rewriting. The addition has the same type and wrapping semantics, so the transformation preserves our operation's specified result. Printing this lowered module produces a program using standard `arith` and `func` operations that an appropriately configured MLIR toolchain can continue lowering to LLVM and machine code. Python objects never cross that boundary; their textual representation does.

**Check the boundary.** Changing one operand to `i64` violates the schema and should fail structural verification. Replacing addition with subtraction would pass the same type checks but change the program's meaning. Detecting the latter needs a semantic test or proof, not merely a shared schema.

## Concepts and terms

**[1] Sidekick compiler framework.** A framework that works independently but can exchange programs and abstractions with another framework. xDSL favors an interpreted Python implementation for experimentation; MLIR favors a compiled C++ implementation for compiler execution speed. A pipeline may stay entirely in xDSL, hand off to MLIR, or insert xDSL between MLIR stages. These choices do not require identical APIs or object layouts.

**[2] SSA, operations, blocks, and regions.** Static single assignment gives each value one definition, either an operation result or a block argument. An operation records its name, operands, results, compile-time attributes, nested regions, and successors. A block is an ordered sequence of operations; its terminator determines how execution leaves it. A region contains blocks and belongs to an enclosing operation, making structures such as functions and loops explicit. A dialect groups related operations, types, and attributes.

**[3] Textual interchange.** Both frameworks read and write MLIR-style syntax, reconstructing their own objects from the exchanged text. Generic operation syntax records an operation's name, operands, attributes, regions, and types without a dialect-specific shorthand. Types and attributes can still need dedicated parsers and printers. Compatibility therefore depends on supported syntax, dialect definitions, and matching versions, not just agreeing that a file is MLIR.

**[4] PyRDL.** A Python-embedded interface for declaring operation and attribute constraints. Decorators process class definitions to supply accessors, verifiers, and parsing/printing support. Definitions describe permitted structure rather than executable arithmetic or memory semantics. Exportable declarations can be converted into IRDL through Python introspection, while imported definitions can generate corresponding Python classes.

**[5] IRDL dialect.** A compiler IR that represents dialect definitions as data. Its operations declare dialects, operations, types, attributes, and constraints over their components. For example, a type constraint can require exactly `i32`, while another allows one of several types. Because both frameworks understand this definition language, they can exchange a schema through the same textual mechanism used for ordinary programs and register it dynamically.

**[6] Multi-level compilation and rewriting.** A compiler pipeline preserves useful domain-specific operations until it is ready to lower them into more general operations. A rewrite replaces operations and updates the SSA references to their results; later passes can process the replacement dialect. In the example, Python handles `tiny.add`, while existing MLIR passes handle the standard operations left behind. Pass implementations are separate from dialect schemas, so importing a schema does not import its optimization passes.

**[7] Limits of sharing and verification.** The paper's IRDL interchange cannot preserve arbitrary Python data representations or constraints written in C++. Some imported native constraints are replaced by a permissive constraint accepting any value, weakening structural validation. Successfully parsing and printing an operation is therefore weaker than fully understanding or verifying it. The paper's performance comparisons concern compiler development and execution costs, not a guarantee that every xDSL pipeline produces equally fast machine code. xDSL does not provide a general proof that user-written rewrites preserve semantics.
