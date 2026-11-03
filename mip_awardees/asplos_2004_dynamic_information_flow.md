# Secure Program Execution via Dynamic Information Flow Tracking

**Summary by:** GPT 6 Astra

**Author:** G. Edward Suh, Jae W. Lee, David Zhang, Srinivas Devadas

**Source:** ASPLOS 2004; ASPLOS Influential Paper Award 2014

**Link:** https://doi.org/10.1145/1024393.1024404

## Key insight

Input data can remain dangerous after it has been copied or transformed. Hardware-supported tags can follow selected dependencies and stop suspicious uses of derived values, such as treating externally supplied bytes as a control-transfer target.

## Basic idea

A trusted execution monitor marks selected input channels as potentially untrusted [1]. Security tags [2] accompany values through registers and memory, with propagation controlled by a policy [3]. Hardware checks designated sensitive uses and raises a trap for software adjudication [4]. The paper targets particular corruption and takeover attacks; its dependency tracking is not a proof of arbitrary information-flow noninterference.

## Illustrative example

**Introduce tagged input.** A server reads a message from an untrusted network source. The monitor tags its bytes as spurious. A vulnerable copy operation places too many of those bytes into a stack buffer and overwrites a saved return address.

**Preserve the origin.** The copy stores both the bytes and their tags. When the return address is later loaded into a register, its tag follows the loaded value. The system can therefore detect its origin at the eventual control transfer, rather than relying on a check at the earlier input call.

**Check the sensitive use.** Under a policy forbidding unchecked spurious control targets, the indirect transfer traps before using the overwritten address. The software handler evaluates the policy and rejects the unauthorized use. The scheme has detected the dangerous consequence; it has not prevented the out-of-bounds write itself or automatically repaired other damaged data.

**Distinguish legitimate dependence.** Applications also compute array offsets from input. Whether an address-derived result receives a tag depends on the selected propagation rules. Propagating every possible dependence can reject legitimate operations, while omitting dependencies can leave attacks uncovered. A program branch on input does not automatically taint everything in its branch body in this paper's implementation.

## Concepts and terms

**[1] Input classification.** Trusted software identifies which data sources require tracking. A spurious tag records possible influence from such a source; it does not prove that the particular value is malicious. Untagged attacker-controlled inputs weaken the intended protection.

**[2] Security tag.** The design associates a tag with each register and with byte-granularity memory data. Tags are part of process state and must be maintained across loads, stores, and context switches. Metadata protection and correct tag handling are therefore part of the trusted implementation.

**[3] Propagation policy.** Rules select how copying, arithmetic, load-address, and store-address dependencies affect tags. A propagation-control register configures selected behaviors. The paper gives special treatment to operations such as pointer addition and register clearing. It explicitly does not track general control dependence, so its guarantees must not be described as complete dynamic information-flow security.

**[4] Sensitive-use check and scope.** Using a tagged value as an instruction, code pointer, or selected data pointer can trigger a security exception. Software distinguishes permitted uses from policy violations. The mechanism depends on the chosen sources, propagation, checks, and trusted handler; it does not detect every data-only logic attack or physical side channel.
