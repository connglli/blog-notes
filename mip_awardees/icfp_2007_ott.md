# Ott: Effective tool support for the working semanticist

**Summary by:** GPT 6 Astra

**Author:** Peter Sewell, Francesco Zappa Nardelli, Scott Owens, Gilles Peskine, Thomas Ridge, Susmit Sarkar, and Rok Strniša

**Source:** ICFP 2007; SIGPLAN Most Influential ICFP Paper Award 2017.

**Link:** https://doi.org/10.1145/1291151.1291155

**Code:** [Ott implementation](https://github.com/ott-lang/ott)

## Key insight

One structured language specification can generate both readable mathematical notation and proof-assistant definitions. Making grammar, binding, and rule structure explicit catches inconsistencies that unstructured typesetting cannot detect.

## Basic idea

Ott is a metalanguage [1] for defining object-language grammars and inference rules [2] in notation close to published semantics. Binding specifications [3] identify which variables bind in which subterms and support generated substitution and free-variable operations. The tool parses symbolic terms, checks structural consistency, and generates several target representations [4], including typeset rules and proof-assistant code. These checks validate the shape of a definition, not its mathematical correctness or a theorem such as type safety.

## Illustrative example

**Language.** Define a tiny expression language with variables, integer constants, addition, and `let name = value in body`. The let-bound name is in scope in `body`, but not in its initializing `value`.

A typing rule checks the initializer under the original environment, then checks the body under an environment extended with the bound name's type. An evaluation rule first evaluates the initializer and then substitutes its result into the body.

**One specification.** The Ott grammar declares these constructs and their argument categories. The binding clause explicitly attaches the bound name to the body's scope. The rule premises and conclusion use symbolic expressions parsed by this grammar.

If a rule accidentally puts a type where a term is required, the structural check can report that mismatch. If it instead omits a necessary premise while remaining syntactically well formed, Ott cannot infer that the rule is wrong.

**Generated outputs.** A typesetting backend renders the same typing rule for a paper. A proof-assistant backend generates corresponding syntax constructors and an inductively defined typing relation. For the term `let count = 4 in count + 3`, both outputs describe the same declared structure.

**Binding boundary.** Substitute an expression with free variable `outer` into a body that contains a binder also named `outer`. Correct capture-avoiding substitution must first rename that binder or otherwise account for the collision. The paper distinguishes its concrete-name substitution machinery from its general account of alpha-equivalence [5] and capture avoidance. Generated helpers must be used with the representation's stated freshness conditions, not assumed to solve every binding issue automatically.

## Concepts and terms

**[1] Metalanguage.** A language for specifying another language's syntax and semantics. The language being specified is the object language.

**[2] Inference rule.** A structured statement that derives a judgment when its premises hold, such as a typing or reduction judgment.

**[3] Binding specification.** A declaration of which name occurrences introduce variables and which subterms are within their scope. It supplies information not recoverable from an unannotated grammar alone.

**[4] Target representation.** Generated code or notation for a selected backend. Backend-specific representations can differ while being generated from the same source definition.

**[5] Alpha-equivalence.** Equality of expressions up to consistent renaming of bound variables. Capture-avoiding substitution preserves the distinction between a free variable and an unrelated binder with the same spelling.

