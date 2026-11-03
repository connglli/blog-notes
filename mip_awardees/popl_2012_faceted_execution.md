# Multiple facets for dynamic information flow

**Summary by:** GPT 6 Astra

**Author:** Thomas H. Austin and Cormac Flanagan

**Source:** POPL 2012; SIGPLAN Most Influential POPL Paper Award 2022.

**Link:** https://doi.org/10.1145/2103656.2103677

**Code:** [ZaphodFacets browser implementation](https://github.com/taustin/ZaphodFacets)

## Key insight

A value can hold different results for differently authorized observers. Keeping these alternatives within one execution handles implicit flows without forcing every observer to share the secret-dependent result.

## Basic idea

Faceted execution represents a protected value by a decision tree of facets [1], indexed by principals' authority. Operations lift over these trees, while a program-counter context [2] records which alternatives are being evaluated. Branches on a faceted condition may execute both alternatives, updating only the corresponding views of memory. Projection [3] relates each observer's view to a separate ordinary execution and supports termination-insensitive noninterference [4], not a general timing-security guarantee.

## Illustrative example

**Setup.** A secret integer has value 8 for an authorized observer and a public substitute 0 for an unauthorized observer. Represent it as `<Owner ? 8 : 0>`. A public variable `status` starts at 1. The program tests whether the secret exceeds 5, sets `status` to 4 if so, then returns `status + 2`.

**Branch evaluation.** Comparing the faceted secret with 5 gives `<Owner ? true : false>`. Since the current context has not chosen an Owner view, evaluation splits. In the authorized branch, the assignment changes only the Owner-visible component of `status`. The other component keeps its old value.

After the branches merge, `status` is `<Owner ? 4 : 1>`. Adding 2 yields `<Owner ? 6 : 3>`. The public result is 3 even though the real secret caused an assignment in the authorized view.

**Projection.** An authorized observer projects the input to 8 and the result to 6. An unauthorized observer projects the input to 0 and the result to 3. These match the two ordinary executions of the same program on their respective inputs.

Changing the private input from 8 to 2 changes the authorized result from 6 to 3 but leaves the public projected execution unchanged. Shared values need not be duplicated when all their facets coincide.

**Boundary.** Output must also be mediated according to the receiving observer's view. Printing the entire internal facet tree to a public channel would reveal the secret. Nor does the projection argument guarantee equal execution times: branch work and nontermination require separate treatment.

## Concepts and terms

**[1] Facet.** An observer-dependent alternative, written `<k ? private : public>`. Either branch can itself be faceted, allowing combinations of multiple principals' permissions.

**[2] Program-counter context.** A record of positive and negative principal choices made during split evaluation. It restricts which parts of a stored faceted value an assignment may change.

**[3] Projection.** Selecting the private branch for principals an observer may inspect and the public branch for the others. Projecting a faceted execution corresponds to the observer's ordinary execution under the theorem's conditions.

**[4] Termination-insensitive noninterference.** The relevant public results of terminating executions do not depend on changes confined to secrets. It does not rule out every disclosure through whether or how long a computation runs.

