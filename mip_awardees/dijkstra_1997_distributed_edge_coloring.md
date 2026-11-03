# Randomized Distributed Edge Coloring via an Extension of the Chernoff-Hoeffding Bounds

**Summary by:** GPT 6 Astra

**Author:** Alessandro Panconesi, Aravind Srinivasan

**Source:** SIAM Journal on Computing 26(2), 1997; Edsger W. Dijkstra Prize in Distributed Computing, 2019

**Link:** https://doi.org/10.1137/S0097539793250767

## Key insight

Random choices can make steady local progress even when their outcomes are dependent, provided the analysis bounds the relevant joint probabilities instead of assuming independence.

## Basic idea

The algorithm computes distributed edge colorings [1] by recursively partitioning a graph and coloring the resulting bipartite graphs [2]. In its main subroutine, one side proposes distinct random colors on incident edges, and the other side resolves collisions by lotteries. Winners retain colors while losers repeat with fresh palettes [3], followed by a cleanup coloring. Extended concentration bounds [4] control residual degrees despite dependencies between collision outcomes.

## Illustrative example

**Subproblem.** Take a bipartite graph with bottom vertices X,Y and top vertices U,V, with all four cross edges present. Each vertex knows its side. The following small phase illustrates the main subroutine; the complete algorithm may send such a low-degree graph directly to cleanup.

**Propose.** Each bottom vertex draws colors without replacement from `{red,blue}`. Suppose X proposes red on X-U and blue on X-V, while Y proposes red on Y-U and blue on Y-V. Proposals are locally conflict-free at X and Y, but U has two red proposals and V two blue proposals.

**Resolve.** U chooses X-U as its red winner; V chooses Y-V as its blue winner. Keep those edges colored. Remove the colors from Y-U and X-V. The remaining edges are disjoint and could both receive a fresh green color during cleanup, giving a valid three-coloring.

**Analyze.** Whether one edge loses is related to other outcomes because each bottom vertex assigns distinct colors. Treating all loss indicators as independent would therefore be unjustified. The paper's joint-event bounds yield tail bounds on how many edges remain incident to a vertex. Fresh palettes prevent an edge colored in a later phase from conflicting with an earlier winner. General graphs are reduced by random vertex bipartitions, and their same-side subgraphs are handled recursively. The result aims for few colors with high probability, not an exact minimum coloring on every graph.

## Concepts and terms

**[1] Edge coloring.** Assign a color to every edge so edges sharing an endpoint differ; it models conflict-free communication slots.

**[2] Bipartite graph.** Vertices have two known sides and every edge crosses between them.

**[3] Palette.** A set of allowed colors; fresh palettes are disjoint from colors used in earlier phases.

**[4] Concentration bound.** An upper bound on large deviations from typical random behavior. The paper extends Chernoff-Hoeffding-style reasoning to variables satisfying specified joint-probability bounds, not arbitrary dependence.
