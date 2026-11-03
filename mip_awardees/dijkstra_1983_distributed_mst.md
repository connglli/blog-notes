# A distributed algorithm for minimum-weight spanning trees

**Summary by:** GPT 6 Astra

**Author:** R. G. Gallager, P. A. Humblet, and P. M. Spira

**Source:** ACM Transactions on Programming Languages and Systems 5(1), 1983; Edsger W. Dijkstra Prize in Distributed Computing 2004.

**Link:** https://doi.org/10.1145/357195.357200

## Key insight

Each partial tree can safely grow through its cheapest outgoing edge. Fragment levels coordinate these local choices so asynchronous growth does not require repeated global knowledge or uncontrolled repeated searches.

## Basic idea

The algorithm constructs a minimum spanning tree [1] in a connected undirected network with distinct edge weights. Nodes organize into fragments [2], test boundary edges, and report a fragment's minimum outgoing edge toward its core [3]. Equal-level fragments sharing that edge merge and increase their level; a lower-level fragment can be absorbed into a higher-level one. Edge states [4] and deferred messages distinguish an internal edge from a boundary edge despite concurrent fragment changes.

## Illustrative example

**Graph.** Four nodes have edges `A-B:1`, `C-D:2`, `B-C:4`, `A-C:6`, and `A-D:7`. The numbers are distinct weights. Nodes initially know only adjacent edges.

**Initial fragments.** A and B select their shared minimum edge of weight 1, forming a level-1 fragment with that edge as its core. C and D do the same on weight 2. Singleton fragments start at level 0.

**Find an outgoing edge.** Within fragment `{A,B}`, A tests candidate non-tree edges and B tests its edge to C. Tests carry the fragment identity and level. A matching identity reveals an internal edge and causes rejection; a suitable different identity confirms a boundary edge. A test aimed at a fragment whose level is still too low may have to wait.

Local candidates are combined by reports along the fragment tree. B reports weight 4; A's best outgoing candidate has weight 6. The core consequently selects edge B-C. Fragment `{C,D}` also selects B-C, since its alternatives have weights 6 and 7.

**Merge.** The two level-1 fragments join across their common minimum edge and form a level-2 fragment. Initialization messages distribute the new identity and level. Further tests find no outgoing edge, so the resulting tree contains weights 1, 2, and 4, totaling 7.

The cut property justifies adding each selected edge: it is the unique minimum crossing the fragment boundary. Level rules provide an additional implementation discipline; merely sending simultaneous connect requests without coordinating changing identities would omit an important part of the algorithm.

## Concepts and terms

**[1] Minimum spanning tree.** A connected, cycle-free set of edges covering all vertices with minimum total weight. The cut property makes a uniquely lightest edge across a cut safe to include.

**[2] Fragment.** A connected piece of the developing spanning tree, carrying an identity and level. Merging equal levels raises the level; absorption into a higher level leaves that level unchanged.

**[3] Core.** The edge joining two equal-level fragments when they merge. Its weight identifies the new fragment, and its endpoints coordinate the fragment's search.

**[4] Edge state.** A local classification as Branch, Rejected, or Basic: respectively part of the fragment tree, known internal non-tree edge, or not yet classified. Basic edges are tested in weight order.

