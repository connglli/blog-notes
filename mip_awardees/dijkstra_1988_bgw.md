# Completeness Theorems for Non-Cryptographic Fault-Tolerant Distributed Computation

**Summary by:** GPT 6 Astra

**Author:** Michael Ben-Or, Shafi Goldwasser, Avi Wigderson

**Source:** STOC 1988; Edsger W. Dijkstra Prize in Distributed Computing, 2023

**Link:** https://doi.org/10.1145/62212.62213

## Key insight

Compute on secret shares instead of reconstructing intermediate values, refreshing the sharing after multiplication so secrecy and reconstructibility survive a long computation.

## Basic idea

BGW evaluates arithmetic circuits [1] over polynomial secret shares [2]. Addition is local, but multiplication raises polynomial degree, requiring private degree reduction and randomization [3]. With synchronous private channels, the paper gives privacy against fewer than half the participants behaving passively, and privacy plus resilience against fewer than one third actively cheating [4]. These are information-theoretic guarantees under the communication model, not claims that ordinary unprotected networks provide private channels.

## Illustrative example

**Share.** For three participants and one passive observer, work modulo 17. Share input two using `f(z)=2+3z`, and input four using `g(z)=4+2z`. At public coordinates one, two, and three, the shares are `(5,8,11)` and `(6,8,10)`. Each participant sees only its own pair. Random slopes, rather than these particular illustrative slopes, provide privacy.

**Multiply.** Local products are `(13,13,8)`, evaluations of `h(z)=8+16z+6z^2` modulo 17. Its constant term is the desired product eight, but its degree is two. Repeatedly multiplying such encodings would eventually require more evaluation points than the population provides.

**Reduce privately.** Evaluation and interpolation are linear transformations. Interpolate coefficients, discard coefficients above degree one, then evaluate again, performing this fixed linear transformation on privately shared data. For each output coordinate, re-share the input values, form the prescribed weighted sum of shares locally, and send the resulting shares only to that output's recipient for reconstruction. The paper adds independently shared zero-constant random polynomials before reduction, preserving eight while refreshing the retained coefficients.

**Result.** A possible refreshed result is `k(z)=8+10z`, giving shares `(1,11,4)`. Any two reconstruct eight; one share does not reveal it when the slope is uniformly hidden. For this illustration, `2*k(1)-k(2)=2-11=8 mod 17`. Malicious participants require the paper's verification and fault-tolerance machinery, and three participants do not satisfy its one-active-fault threshold.

## Concepts and terms

**[1] Arithmetic circuit.** A computation composed of additions and multiplications over a finite field, where nonzero elements have multiplicative inverses.

**[2] Polynomial secret sharing.** Encode a secret as the constant term of a random degree-t polynomial and give participants distinct nonzero evaluations; t evaluations reveal no information about the constant.

**[3] Degree reduction and randomization.** Convert a product sharing back to the required degree while preserving its secret and refreshing hidden coefficients through communication.

**[4] Passive versus active corruption.** Passive participants reveal their views but follow the protocol; active participants may send false data or stop cooperating.
