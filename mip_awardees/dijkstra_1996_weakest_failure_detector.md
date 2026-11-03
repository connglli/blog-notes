# The weakest failure detector for solving consensus

**Summary by:** GPT 6 Astra

**Author:** Tushar Deepak Chandra, Vassos Hadzilacos, and Sam Toueg

**Source:** Journal of the ACM 43(4), 1996; Edsger W. Dijkstra Prize in Distributed Computing 2010.

**Link:** https://doi.org/10.1145/234533.234549

## Key insight

To prove failure information necessary, extract it from any detector that already enables consensus. The extraction shows that such a detector must contain enough information to eventually identify one common correct process.

## Basic idea

Failure-detector reducibility [1] compares detectors by whether one can emulate another. Given any detector and algorithm solving consensus, the paper samples detector outputs into a directed acyclic graph [2] and simulates compatible executions. Decision valence [3] and finite decision gadgets [4] reveal a process that must be correct. All correct processes eventually choose the same such process, implementing Omega [5]. Omega implements the paper's eventually weak detector, diamond-W [6], which suffices for consensus with a correct majority and is therefore weakest in that environment.

## Illustrative example

**Sample.** Process A queries its detector and obtains output `dA`. It sends a record containing A's identity, that output, and a local query number. B receives the record and later obtains `dB`, adding a directed edge from A's sample to B's sample. Processes repeatedly exchange and merge these graphs.

The edge records observed ordering, not a synchronized clock reading. A graph path supplies a possible sequence of detector values for simulated consensus steps.

**Simulate.** Consider three processes and the input assignments `000`, `100`, `110`, and `111`. For each assignment, enumerate compatible schedules, branching over permitted message deliveries. In the limiting forest, tag a state with decisions reached by correct processes in its descendants.

Suppose, in the limiting simulation forest, neighboring roots `000` and `100` are respectively 0-valent and 1-valent. Only A's input differs. If A were faulty, the correct processes could continue without further steps by A and could not maintain this necessary distinction. The extraction argument therefore identifies A as correct.

If a critical root is bivalent instead, the proof uses a finite fork or hook whose branches force opposite decisions and identifies its deciding process. This case is needed when no adjacent purely univalent transition supplies the answer.

**Converge.** A simulator cannot know which processes are correct, so it tags its finite forest using its own simulated decisions. At correct simulators these tags converge to the limiting tags. A fixed selection rule over the growing forest eventually settles on a finite witness shared by all correct processes, whose outputs then permanently identify the same correct process.

To implement diamond-W from Omega, suspect everyone except the currently selected process. Once the selection stabilizes, every crashed process is suspected and the selected correct process is protected. The extraction is a necessity construction, not an efficient practical leader-election algorithm.

## Concepts and terms

**[1] Reducibility.** Detector D is at least as strong as D' when an algorithm using D can produce outputs satisfying D' in the relevant failure environment.

**[2] Sample graph.** A directed acyclic graph of process identities, detector outputs, and local sample numbers, with edges recording observed temporal precedence.

**[3] Decision valence.** The set of decisions reachable from a simulated state. A bivalent state permits both Boolean decisions; a univalent state permits only one.

**[4] Decision gadget.** A finite fork or hook in the simulation tree exposing a process whose step separates opposite decision outcomes. The proof establishes that this deciding process cannot be faulty.

**[5] Omega.** An eventual-leader detector: after some unknown time, all correct processes permanently output the identity of the same correct process. Before then, outputs may disagree or identify faulty processes.

**[6] Diamond-W.** Weak completeness plus eventual weak accuracy: every crashed process is eventually permanently suspected by some correct process, and some correct process is eventually never suspected by any correct process.

