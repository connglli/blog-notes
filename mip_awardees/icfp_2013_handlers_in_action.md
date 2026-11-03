# Handlers in action

**Summary by:** GPT 6 Astra

**Author:** Ohad Kammar, Sam Lindley, and Nicolas Oury

**Source:** ICFP 2013; SIGPLAN Most Influential ICFP Paper Award 2023.

**Link:** https://doi.org/10.1145/2500365.2500590

**Code:** [Effect-handler implementations and examples](https://github.com/slindley/effect-handlers)

## Key insight

An effectful program can name operations without fixing their interpretation. A handler supplies that interpretation by deciding how each operation resumes the rest of the computation.

## Basic idea

Algebraic operations [1] describe requests such as state access, failure, or choice. A handler [2] provides an operation clause receiving the request arguments and a continuation [3], plus a clause for ordinary return. Resuming zero, one, or several times gives different interpretations of the same operation. Effect typing [4] tracks the operations a computation may request and prevents them from accidentally reaching execution without a handler.

## Illustrative example

**Computation.** A program requests a choice between 3 and 8, adds 2 to the chosen number, and returns the result. It specifies the choice operation but does not decide whether choice means taking the first value, sampling randomly, or exploring all alternatives.

**First-choice interpretation.** The handler for choice receives arguments 3 and 8 and a continuation `k`. Here `k(value)` represents the remaining addition and return, under the handler. Invoke `k(3)` once. With an identity return clause, the final result is 5.

**All-results interpretation.** Change only the handler. Its return clause wraps an ordinary result in a singleton list. Its choice clause resumes both alternatives and concatenates their results: `k(3) ++ k(8)`. The two continuations produce `[5]` and `[10]`, yielding `[5,10]`.

These resumes repeat the rest of the handled computation. If that remainder contained another choice, the handler would interpret it too. If it contained other effects, their handling and ordering would matter; duplicating a continuation is not a claim that arbitrary external effects can be silently duplicated without consequences.

**Failure and typing.** A failure operation can be interpreted by a clause returning an empty result list without resuming its continuation. The type-and-effect account records whether choice and failure can occur and what remains after handling. A complete program needs suitable handlers for the remaining operations.

A rough implementation can represent computations as either a returned value or an operation node carrying arguments and a continuation. A handler recursively interprets this structure, wrapping resumed continuations so subsequent operations are handled according to the chosen semantics.

## Concepts and terms

**[1] Algebraic operation.** An abstract request with specified parameter and result types. Its declaration does not fix the concrete behavior used to produce a result.

**[2] Handler.** An interpreter for selected operations and normal return. Its clauses can change the result representation, such as turning a single result into a list of possibilities.

**[3] Continuation.** A representation of the computation remaining after an operation, parameterized by the operation's returned value. The all-results handler uses it nonlinearly by resuming it twice.

**[4] Effect typing.** Static tracking of which operations may occur and which handlers can interpret them. It complements ordinary result typing by accounting for unhandled requests.

