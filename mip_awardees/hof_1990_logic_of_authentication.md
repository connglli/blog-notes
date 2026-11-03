# A Logic of Authentication

**Summary by:** GPT 6 Astra

**Author:** Michael Burrows, Martín Abadi, and Roger Needham

**Source:** ACM Transactions on Computer Systems 8(1), 1990; SIGOPS Hall of Fame Award 2007

**Link:** https://doi.org/10.1145/77648.77649

## Key insight

An authentication exchange changes what participants are justified in believing, not just which encrypted strings they have received. Making those beliefs and their premises explicit exposes missing freshness and trust assumptions.

## Basic idea

BAN logic translates protocol messages into an idealized form [1] and records each principal's initial beliefs [2]. Message-meaning rules [3] derive who once said a protected statement from beliefs about its key. Nonce verification [4] uses freshness to distinguish current belief from an old utterance, and jurisdiction [5] permits accepting a statement from a trusted authority. The result is a derivation about the idealized protocol under its premises, not an automatic proof that arbitrary ciphertext encodings or implementations are secure.

## Illustrative example

**State assumptions.** Client A trusts server S to authorize which session key is suitable for talking to B. A believes long-term key `K_AS` is shared only with S, and A has generated fresh challenge `n`. Let X mean "key k is suitable for communication between A and B." S returns a protected message whose idealized content is `(n, X)` under `K_AS`.

**Attribute the message.** After receiving and decrypting the message, A applies the message-meaning rule: because it believes the key is shared with S, and the message is not A's own reflected output, A believes that S once said `(n, X)`. This conclusion alone permits an old statement; it does not establish that S currently endorses X.

**Use freshness.** A's fresh challenge makes the containing statement fresh under the logic's freshness rule. Nonce verification then gives A the belief that S currently believes `(n, X)`, and hence that S believes X. If the received nonce did not match the current challenge, this step would lack its premise.

**Apply authority.** A also believes that S controls assertions of the relevant key-authorization form. The jurisdiction rule combines that authority with S's current belief in X, allowing A to believe X. Without the authority premise, an authenticated statement would establish what S said, not that A should accept its truth.

**Inspect the modeling obligation.** The concrete message format must actually bind `n`, A, B, and k as the idealized statement assumes. Reading more meaning into a message than its encoding and checks justify invalidates the reasoning. The protocol must also satisfy the cryptographic and origin assumptions behind message meaning. A derivation does not make those assumptions true merely by listing them.

This one exchange illustrates the rule chain; it does not show mutual authentication or key confirmation by B, because B has not participated. Those are different desired beliefs and require additional justified protocol steps.

## Concepts and terms

**[1] Idealization.** Replacing concrete messages with logical statements representing their justified meaning. It is a substantive modeling step, not a purely syntactic erasure of bytes.

**[2] Belief.** A statement a principal is entitled to treat as true under the analysis. Nested belief, such as A believing that S believes X, differs from A believing X itself.

**[3] Message meaning.** Rules inferring an authenticated origin from a received protected message and assumptions about the relevant key or secret. They include conditions preventing a principal from attributing its own message to someone else.

**[4] Nonce verification.** A rule combining freshness and attributed utterance to infer current belief. Freshness excludes messages from earlier protocol runs.

**[5] Jurisdiction.** Trust that another principal is authoritative for a class of assertions. It is distinct from authenticating that principal's messages.
