# Combinators for bidirectional tree transformations: A linguistic approach to the view-update problem

**Summary by:** GPT 6 Astra

**Author:** J. Nathan Foster, Michael B. Greenwald, Jonathan T. Moore, Benjamin C. Pierce, and Alan Schmitt

**Source:** POPL 2005; SIGPLAN Most Influential POPL Paper Award 2015.

**Link:** https://doi.org/10.1145/1040305.1040325

**Code:** [Boomerang, a follow-on lens implementation](https://www.engineering.upenn.edu/~harmony/)

## Key insight

Updating a simplified view requires both the edited view and the original source, because the view may omit information. A lens pairs extraction and update functions, and composition preserves their consistency laws.

## Basic idea

A lens [1] has a get function that extracts an abstract view and a put function that incorporates an edited view into an old concrete source. Two round-trip laws [2] constrain their agreement without requiring get to be invertible. The paper builds a language of lens combinators [3] for trees, so a single expression describes both directions. Types restrict acceptable inputs and outputs; partial functions and a distinguished missing source account for unsupported inputs and creation of new structure.

## Illustrative example

**Setup.** Represent one contact as an edge-labeled tree with fields `name`, `phone`, and `note`. Its values are `"Iris"`, `"410"`, and `"prefers email"`. A directory editor should expose only `name` and `phone`, preserving the private note.

**Extraction and update.** Define get to retain the two visible fields. Define put to take replacement values for those fields and reuse the old `note`. Editing the phone to `"720"` therefore produces `{name: "Iris", phone: "720", note: "prefers email"}`.

Putting back the unedited view returns the original tree, satisfying GetPut. Extracting a view after an update returns exactly the edited visible fields, satisfying PutGet. A put operation that always resets the note to an empty string would fail the first law even though its visible output looked correct.

**Composition.** Add another lens that exposes only the phone from the two-field directory view. To propagate an edit through the composition, first get the intermediate directory from the original contact, put the new phone into that intermediate view, and then put the modified directory into the original contact.

For `"930"`, the inner update preserves `name = "Iris"`; the outer update preserves the note. This describes a mechanical implementation of composed put, rather than attempting to invert a chain of lossy getters.

If no old contact exists, put must use its explicitly defined creation behavior, for example a default note. The ordinary round-trip check for an existing source does not determine that default.

## Concepts and terms

**[1] Lens.** A pair of partial functions `get: C -> A` and `put: A x (C or missing) -> C`. The concrete source `C` can contain information absent from the abstract view `A`.

**[2] Round-trip laws.** GetPut requires `put(get(c), c) = c` when get is defined. PutGet requires `get(put(a, c)) = a` when put is defined. The paper additionally studies a stronger PutPut law, but it is not part of basic well-behavedness.

**[3] Lens combinator.** An operation that constructs a lens from smaller lenses, supplying both get and put implementations and checking their compatibility. The tree language includes composition, projection, mapping, and structural operations.

