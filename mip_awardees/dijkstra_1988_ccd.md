# Multiparty Unconditionally Secure Protocols

**Summary by:** GPT 6 Astra

**Author:** David Chaum, Claude Crépeau, Ivan Damgård

**Source:** STOC 1988; Edsger W. Dijkstra Prize in Distributed Computing, 2023

**Link:** https://doi.org/10.1145/62212.62214

## Key insight

Distributed commitments to secret values and their shares let participants verify computations without revealing intermediate secrets or relying on computational hardness assumptions.

## Basic idea

The protocol assumes synchronous authenticated private channels and fewer than one third faulty participants. It builds verifiable secret-sharing commitments, called blobs [1], using polynomial shares and cut-and-choose checks [2]. Robust double blobs [3] bind participants to their shares so computation can continue despite misconduct. Boolean XOR and AND gates [4] are evaluated on these commitments, with masked degree conversion after multiplication; checking errors can be made small without computational assumptions.

## Illustrative example

**Inputs.** Four participants tolerate one malicious participant. They want the AND of hidden bits a and b. Encode each bit as the constant term of a random degree-one polynomial over a characteristic-two field with more than four elements, distributing one evaluation to each participant.

**Commit and check.** Participants also commit to the shares they hold. For consistency tests, create fresh auxiliary commitments and let an unpredictable challenge choose between opening an auxiliary value and opening its masked combination with the original. Revealing only the challenged form protects the original secret; repeated tests make inconsistent preparations unlikely to escape detection. Robust double-blob construction supplies the recovery and consistency properties needed when a participant refuses cooperation.

**Gate.** XOR adds corresponding shares, since field addition agrees with XOR on embedded bits. For AND, participants multiply their shares and prove those products consistent with their committed inputs. The resulting polynomial has degree two, so it cannot simply be reused as an ordinary degree-one encoding indefinitely.

**Masked conversion.** Prepare verified high-degree and low-degree sharings of the same hidden random bit r. Open only the XOR of the product bit and the high-degree sharing of r. If the opened bit is zero, retain the low-degree sharing of r; if it is one, complement that sharing. For illustrative hidden values `a=1`, `b=0`, and `r=1`, the opened bit is one and complementing r yields zero, the required AND. The opening reveals a masked bit, not a or b. This depends on correct preparation of the masks and commitments, not merely on naming them secret.

## Concepts and terms

**[1] Blob.** A distributed commitment hiding a value while binding its creator to a unique opening, built from polynomial secret sharing.

**[2] Cut-and-choose.** Commit before an unpredictable challenge, then reveal one of several linked checks; repetition limits cheating probability.

**[3] Robust double blob.** A commitment structure including commitments to shares and consistency checks that support reliable recovery and computation.

**[4] Boolean gates.** XOR and AND suffice to express Boolean computations; addition and multiplication implement them on bits in a characteristic-two field.
