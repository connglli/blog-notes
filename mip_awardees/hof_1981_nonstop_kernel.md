# A NonStop Kernel

**Summary by:** GPT 6 Astra

**Author:** Joel F. Bartlett

**Source:** SOSP 1981; SIGOPS Hall of Fame Award 2013

**Link:** https://dl.acm.org/citation.cfm?id=806587

## Key insight

A service can survive a processor failure when a backup process receives the state needed to continue it and clients address the service independently of its current processor. Retried requests also need remembered outcomes, or failover can repeat non-repeatable work.

## Basic idea

The Tandem kernel uses processes and message passing [1] as the basis for accessing resources across processors. A process pair [2] contains a primary that serves requests and a backup on another processor. Application-specific checkpoints [3] transfer the request and state needed for takeover. Symbolic names redirect clients to the active half, while sequence numbers and saved results suppress duplicate requests [4]. Fault tolerance therefore includes both kernel mechanisms and a service protocol designed to survive interruption at each step.

## Illustrative example

**Request.** A client asks a disk service to insert record `invoice-17` into a keyed file. This is not safely repeatable: inserting the same key twice can produce an error or a second external effect. The request carries sequence number 8. The service is named independently of the processor currently hosting its primary S; backup S' runs elsewhere.

**Checkpoint.** S checks whether request 8 already has a saved outcome. If not, it reads the affected disk block, constructs the block containing the new record, and checkpoints the request and new block to S'. After writing the block, it checkpoints completion information and advances the request sequence state before returning the result under the protocol's ordering.

**Lose the reply.** Suppose the update completed but the reply never reached the client, and S's processor then fails. S' takes over with enough state to distinguish work needing completion from work already completed. The client retries request 8 through the symbolic service name. The replacement returns the remembered outcome rather than performing a fresh logical insertion.

If the primary fails before the write finishes, the backup can use the checkpointed block image to complete the operation. Rewriting that prepared block is different from re-executing an arbitrary non-idempotent operation from scratch. The server protocol must decide which state and outcomes to retain; the kernel cannot infer this for every service.

**Reestablish redundancy.** A surviving primary can create a replacement backup on another processor and checkpoint current state to it. During degraded operation, the service may have less protection against an additional failure. The design assumes its failure-detection, communication, storage, and checkpoint mechanisms satisfy their contracts; a process pair does not make arbitrary software bugs or simultaneous loss of all relevant state harmless.

## Concepts and terms

**[1] Message passing.** Requests and replies exchange values rather than exposing one shared mutable address space across processors. Kernel primitives track and clean up exchanges when processes or processors fail.

**[2] Process pair.** A named primary/backup arrangement in which the backup can assume the primary's role after failure. Naming hides which process currently provides the service.

**[3] Checkpoint.** Service-specific state sent to the backup at defined points. It must be sufficient to complete or safely resume an interrupted operation, not merely copy an arbitrary subset of memory.

**[4] Duplicate suppression.** Recognizing a retried request by sequence information and returning its saved status. How many outcomes must be retained depends on the requesting processes and protocol.
