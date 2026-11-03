# Sparse partitions

**Summary by:** GPT 6 Astra

**Author:** Baruch Awerbuch and David Peleg

**Source:** FOCS 1990; Edsger W. Dijkstra Prize in Distributed Computing 2008.

**Link:** https://doi.org/10.1109/FSCS.1990.89571

## Key insight

Local neighborhoods can be preserved without making every node belong to an excessive number of clusters. Carefully merging overlapping clusters trades a bounded increase in radius for a reduction in overlap.

## Basic idea

A locality-preserving cover [1] contains each required neighborhood inside some connected cluster. The paper coarsens [2] an initial cover while controlling cluster radius [3] and overlap degree [4]. Its construction grows a cluster kernel with a surrounding layer until growth slows, emits the kernel, and temporarily excludes the surrounding layer to keep a phase's outputs disjoint. Repeating partial-cover phases covers the remaining input clusters and bounds how many output clusters can contain any one vertex.

## Illustrative example

**Initial neighborhoods.** Take the unit-edge path with vertices 0 through 8. The initial cover consists of the nine closed radius-1 neighborhoods. For example, the neighborhood of 4 is `{3,4,5}`, and that of 0 is `{0,1}`.

An interior vertex belongs to three such neighborhoods. Arbitrarily partitioning the path into disjoint blocks could reduce overlap to one but would split neighborhoods crossing block boundaries.

**Grow a kernel.** Choose the neighborhood of 4 as a seed. It intersects the neighborhoods centered at 2, 3, 4, 5, and 6. Their union is `{1,2,3,4,5,6,7}`. A further surrounding layer reaches the remaining neighborhoods near the path's ends.

With parameter `k = 2`, growth from one participating input cluster to five exceeds the initial threshold `sqrt(9) = 3`; growth from five to nine does not. The inner union can be emitted as the kernel, while the outer layer is reserved rather than immediately emitted with it.

**Finish coverage.** The boundary neighborhoods still need coverage in later phases. To visualize the objective, the three clusters `{0,1,2}`, `{1,2,3,4,5,6,7}`, and `{6,7,8}` form one valid coarsening: every original radius-1 neighborhood lies inside one cluster. Their maximum induced radius is 3, and no vertex appears in more than two clusters. This final choice illustrates the coarsening contract rather than prescribing every tie-breaking choice in the general algorithm.

**Bound.** For an arbitrary input cover `S`, the paper's construction bounds the output radius by `(2k-1) * Rad(S)` and maximum overlap by `2k * |S|^(1/k)`. These are worst-case guarantees for the constructed cover, not the exact overlap of every example.

## Concepts and terms

**[1] Locality-preserving cover.** Connected clusters containing each required neighborhood in full. A cover may overlap; a partition requires disjoint clusters and cannot generally provide the same neighborhood guarantee.

**[2] Coarsening.** Replacing a collection of clusters with another collection such that every original cluster is contained in an output cluster.

**[3] Cluster radius.** The minimum, over possible centers inside a cluster, of the greatest shortest-path distance to its other vertices, measured within the cluster's induced connected graph.

**[4] Overlap degree.** The number of cover clusters containing a vertex. Bounding its maximum controls the worst local participation, not merely the total or average cluster membership.

