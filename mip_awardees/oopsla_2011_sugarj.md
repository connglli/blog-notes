# SugarJ: Library-based Syntactic Language Extensibility

**Summary by:** GPT 6 Astra

**Author:** Sebastian Erdweg, Tillmann Rendel, Christian Kästner, Klaus Ostermann

**Source:** OOPSLA 2011; SIGPLAN Most Influential OOPSLA Paper Award, 2021

**Link:** https://doi.org/10.1145/2048066.2048099

**Code:** [SugarJ](https://github.com/sugar-lang/compiler)

## Key insight

A library can export the syntax used to call it, so importing the library brings its notation into scope along with ordinary definitions.

## Basic idea

Sugar libraries combine grammar extensions [1] with desugaring rules [2]. SugarJ processes a source file one top-level entry at a time, updating the active grammar and transformations when it encounters imports or sugar declarations. The generated Java is compiled normally, while extensions can themselves help define other extensions [3]. Composition is supported, but arbitrary extensions are not guaranteed to be unambiguous or hygienic [4].

## Illustrative example

**Library.** Design a small range library with a Java class `Span` and a notation `span(2 .. 5)`. Its grammar recognizes that expression and builds a syntax node containing the two endpoints. Its desugaring replaces that node with construction of the ordinary Java object representing the half-open interval `[2,5)`.

**Import.** A client begins with ordinary package and import declarations. Before importing the range sugar, the special expression is outside the active grammar. Processing the import adds the grammar production and its transformation rules. A later class declaration containing the notation can then be parsed and translated.

**Expansion.** The generated Java expression uses the fully qualified `Span` class name, avoiding accidental resolution to an unrelated local class. The runtime object contains endpoints two and five; iteration visits two, three, and four. This semantic meaning comes from the chosen library and expansion, not from the punctuation itself.

**Composition.** A second library could add set notation whose element expressions include range expressions. The parser composes the syntax rules, and the desugaring pipeline expands both node kinds. An extension defining convenient notation for grammar rules could itself be imported while defining that second library, illustrating self-applicability. Conflicting syntax or an expansion that accidentally captures a client's identifier still requires attention from the extension author; import-based organization does not prove composition or hygiene correct.

## Concepts and terms

**[1] Grammar extension.** Additional productions defining how new source forms parse into syntax-tree nodes.

**[2] Desugaring.** Translating a convenient surface construct into existing constructs with its intended meaning.

**[3] Self-applicability.** Extensions can be used in the metaprograms that define further extensions.

**[4] Hygiene.** Prevention of accidental identifier capture or binding changes introduced by expansion; the prototype permits more general, unhygienic transformations.
