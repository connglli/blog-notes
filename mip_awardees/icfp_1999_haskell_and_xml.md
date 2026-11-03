# Haskell and XML: Generic combinators or type-based translation?

**Summary by:** GPT 6 Astra

**Author:** Malcolm Wallace and Colin Runciman

**Source:** ICFP 1999; SIGPLAN Most Influential ICFP Paper Award 2009.

**Link:** https://doi.org/10.1145/317636.317794

**Code:** [HaXml library](https://github.com/HaXml/HaXml)

## Key insight

XML can be processed either as a uniform tree or as a datatype generated from its document grammar. The first representation makes generic traversal convenient; the second exposes document structure to ordinary static type checking.

## Basic idea

The paper presents complementary XML-processing methods in Haskell. Generic combinators [1] select, transform, and construct subtrees in a uniform document representation. Type-based translation [2] maps a document type definition, or DTD [3], to algebraic datatypes [4] and generates reading and writing functions. The approaches place structural knowledge in different locations: explicit traversal predicates for generic trees, or generated types and conversions for schema-specific values.

## Illustrative example

**Document shape.** A small catalog contains zero or more items. Each item has a required `label` element and an optional `comment` element. One document contains an item labeled `"spade"` with no comment and another labeled `"rake"` with comment `"long handle"`.

**Generic processing.** Parse the document into element and text nodes. Compose a filter selecting `item` children with another selecting their `label` children, then extract text. The result is the list `["spade", "rake"]`. This traversal can run on documents with unrelated structures, but it must explicitly handle absent labels and unexpected child shapes.

**Typed processing.** A simplified Haskell representation of the same grammar is:

```haskell
data Catalog = Catalog [Item]
data Item = Item Label (Maybe Comment)
newtype Label = Label String
newtype Comment = Comment String

labels :: Catalog -> [String]
labels (Catalog items) =
  [name | Item (Label name) _ <- items]
```

This is an explanatory representation, not the exact naming scheme of the paper's generator. Repetition becomes a list, and the optional component becomes `Maybe`. A sum of alternative content forms would similarly become alternative constructors.

The generated reader must reject a document that cannot be converted to the required shape. After successful conversion, `labels` need not check whether an item's label is absent: the datatype has no such constructor.

**Boundary.** A writer converts the typed values back to XML structure. The type represents the supported DTD structure, not every semantic invariant a catalog might need. For example, requiring all labels to be distinct is not established by `Catalog [Item]`; it needs a separate check. The generic approach remains useful when a stable DTD-specific representation is unavailable.

## Concepts and terms

**[1] Generic combinator.** A reusable function composing document selections or transformations over one uniform tree representation. A selection can return several matching pieces rather than one optional node.

**[2] Type-based translation.** Generating a programming-language representation and conversion functions from a document grammar, allowing application code to pattern-match on typed data.

**[3] DTD.** A declaration of permitted XML elements, attributes, and content arrangements, including sequences, alternatives, optional parts, and repetitions.

**[4] Algebraic datatype.** A type built from named alternatives and products of fields. Lists and optional values encode repeated and optional document components.

