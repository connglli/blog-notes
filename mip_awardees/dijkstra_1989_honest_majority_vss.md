# Verifiable Secret Sharing and Multiparty Protocols with Honest Majority

**Summary by:** GPT 6 Astra

**Author:** Tal Rabin, Michael Ben-Or

**Source:** STOC 1989; Edsger W. Dijkstra Prize in Distributed Computing, 2023

**Link:** https://doi.org/10.1145/73007.73014

## Key insight

Information-theoretic checks can authenticate shares, allowing reconstruction from an honest majority without trusting every submitted value or relying on digital signatures.

## Basic idea

The paper constructs verifiable secret sharing [1] and secure multiparty computation with fewer than half faulty participants. It assumes a synchronous network with private pairwise channels and reliable broadcast [2]. Information checking [3] binds forwarded values to a dealer's distribution, while additional tests handle a dishonest dealer. Security is unconditional [4], but protocols allow an error probability controlled by a security parameter.

## Illustrative example

**Why authentication matters.** Five participants tolerate two faulty parties. Over the field modulo 17, share secret six with `f(z)=6+2z+3z^2`, giving evaluations `(11,5,5,11,6)` at coordinates one through five. Any three correct shares reconstruct the secret, but five unauthenticated shares do not generally suffice to correct two arbitrary false values of a degree-two polynomial.

**Check one share.** To authenticate share eleven from an honest dealer through an intermediary to a receiver, use a separate illustrative field modulo 101. The dealer privately gives the intermediary `(s,y)=(11,9)` and the receiver `(b,c)=(7,74)`, where `c=s+b*y`. The receiver accepts a forwarded pair only if that equation holds modulo 101.

**Forgery.** Changing the value to twelve while retaining y=9 produces 75, so the check fails. The intermediary does not know b and cannot generally choose a matching replacement pair. With uniformly hidden nonzero b, a substituted secret passes this single check with probability at most `1/(101-1)`. This small field illustrates the mechanism, not a practical security setting.

**Dishonest dealer and reconstruction.** A malicious dealer might initially distribute inconsistent check data. The full protocol prepares multiple check vectors and opens a random subset so the intermediary gains evidence about the remaining checks; broadcast coordinates disputes. At reconstruction, authenticated correct shares can be retained and invalid submissions rejected, leaving enough for interpolation under the protocol's error bound. The numerical single-check example alone is not a complete malicious-dealer VSS protocol.

## Concepts and terms

**[1] Verifiable secret sharing.** Distribute a hidden value with guarantees that accepted shares determine a consistent reconstruction despite bounded malicious behavior.

**[2] Reliable broadcast.** All correct recipients receive the same authenticated message from a broadcast invocation; pairwise sending alone does not provide this property.

**[3] Information checking.** Authentication using hidden random checking data rather than assumed computational difficulty; its full form also checks dealer consistency.

**[4] Unconditional security.** Security against computationally unbounded adversaries within the stated channel and corruption assumptions, compatible with a tunably small error probability.
