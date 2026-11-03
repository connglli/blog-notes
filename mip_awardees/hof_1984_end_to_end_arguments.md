# End-To-End Arguments in System Design

**Summary by:** GPT 6 Astra

**Author:** J. H. Saltzer, D. P. Reed, and D. D. Clark

**Source:** ACM Transactions on Computer Systems 2(4), 1984; SIGOPS Hall of Fame Award 2007

**Link:** https://doi.org/10.1145/357401.357402

## Key insight

A lower layer cannot completely implement a function when correctness depends on information available only at the application's endpoints. Lower-layer support can still be valuable, but its role and cost must be judged against the complete end-to-end requirement.

## Basic idea

The end-to-end argument [1] asks where a system function has enough information to establish its actual contract. For reliable file transfer, network delivery alone cannot rule out mistakes in file reads, host memory, or destination storage. End-to-end checking [2] and a retry/commit plan [3] remain necessary even with a reliable transport. Lower-level checks [4] can reduce expensive retries and improve performance, but do not automatically remove the endpoint obligation. The argument is a design method, not a universal prohibition on sophisticated network mechanisms.

## Illustrative example

**Define success.** A backup application must copy file F from A's storage to B's storage so that the stored destination bytes match the intended source version. This is stronger than "every network packet reached B." Assume the application can identify a stable source version for the duration of verification.

**Locate gaps.** A link checksum catches a bit error on one wire. A transport acknowledgment confirms some transport-level receipt. Neither proves that A read the correct source bytes nor that B wrote them correctly to its disk. A memory error after packet validation can still corrupt the destination.

**Check at the boundary.** After B stores the file, it reads the stored bytes and computes the agreed file checksum. A compares that value with the checksum for the intended source contents. The application accepts the copy only when its check passes; otherwise it retries or reports a persistent failure. The checksum must have adequate error-detection strength for the threat model, and its own computation and comparison remain assumptions.

**Retain useful lower-layer work.** Suppose a long transfer crosses a link with occasional corruption. Local retransmission of one damaged packet can be much cheaper than repeating the whole file. Link-level protection is therefore useful even though it is not the final evidence of a correct stored file. Its purpose is to reduce how often the endpoint recovery path is exercised.

**Avoid an overclaim.** A checksum that an adversary can deliberately collide is not an authentication mechanism. A sender comparing a checksum of already-corrupted source data proves a different claim from comparing against a protected intended version. The argument requires defining the true endpoints and the property being checked, not merely placing the word "end-to-end" on a transport API.

The same reasoning applies to functions such as duplicate suppression or delivery receipts when their meaning depends on application actions beyond the network stack. Whether lower layers should help is then a performance and engineering decision under that contract.

## Concepts and terms

**[1] End-to-end argument.** Reasoning that a function requiring endpoint knowledge must be completed at those endpoints, even if intermediate components implement partial versions.

**[2] End-to-end checking.** Verification across the whole path relevant to the requirement, including storage or application processing when those are part of the promised result.

**[3] Retry/commit plan.** A policy for recovering from failed verification and deciding when the application may treat the operation as complete. Detection without an appropriate response is not full reliability.

**[4] Lower-level check.** A mechanism validating a narrower part of the path, such as one transmission hop. It may substantially improve efficiency without proving the application's entire property.
