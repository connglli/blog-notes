# JavaScript instrumentation for browser security

**Summary by:** GPT 6 Astra

**Author:** Dachuan Yu, Ajay Chander, Nayeem Islam, and Igor Serikov

**Source:** POPL 2007; SIGPLAN Most Influential POPL Paper Award 2017.

**Link:** https://doi.org/10.1145/1190216.1190252

## Key insight

Security enforcement must mediate both the script already present in a page and scripts generated while that page runs. A fixed rewriting mechanism can consult a separate stateful policy that accepts, suppresses, or replaces relevant actions.

## Basic idea

The paper defines CoreScript [1], a model of script execution and document generation, and instruments programs to route security-relevant actions through a policy interface [2]. Policies are edit automata [3] whose transitions prescribe permitted replacements. A consistency condition [4] requires a prescribed action to be acceptable under the same policy state. Rewriting also handles higher-order script [5], so dynamically produced document fragments do not become an unmediated route to protected browser operations.

## Illustrative example

**Policy.** Suppose a page may create at most one popup window. Use policy states `unused` and `used`. In `unused`, a popup action is retained and changes the state to `used`. In `used`, another popup is replaced by an empty action and the state remains `used`. All ordinary actions leave this policy state unchanged.

**Instrumentation.** An instrumented popup does not directly invoke the browser operation. It requests advice from the policy interface, updates the policy state as prescribed, and executes the returned action. Starting in `unused`, the first request opens a window; the second produces no popup.

The policy is consistent: the first permitted popup, reconsidered from `unused`, is unchanged and produces the same next state. The empty replacement for the second request is also unchanged when reconsidered from `used`.

**Generated code.** The page then writes a document fragment containing another script that requests a popup. Instrumentation must apply to the executable script contained in this new fragment. Merely checking the original page text would miss it. Once mediated, this third request sees `used` and is suppressed.

This example follows the model's action interface rather than proposing a current-browser JavaScript wrapper. A wrapper around one global function would be insufficient if aliases, generated code, or other entry points could bypass it.

**Guarantee.** A faithful implementation of the rewriting and policy interface restricts modeled action traces according to a consistent policy. The policy itself must express the intended protection, and operations outside CoreScript's modeled scope are not covered by the formal result.

## Concepts and terms

**[1] CoreScript.** A simplified operational model of documents, embedded scripts, and browser actions used to state and prove the rewriting properties. It is not a complete semantics of every JavaScript or browser feature.

**[2] Policy interface.** The trusted boundary through which instrumented code obtains permission or a replacement for a relevant action.

**[3] Edit automaton.** A state machine mapping a policy state and proposed action to a next state and replacement action. Suppression uses an empty action.

**[4] Consistency.** If an action is replaced by another action with next state `q'`, processing the replacement from the original state must retain that replacement and yield the same `q'`.

**[5] Higher-order script.** Code that produces further executable document content during execution. Its generated content must obey the same enforcement discipline as the original script.

