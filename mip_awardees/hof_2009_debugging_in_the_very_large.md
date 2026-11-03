# Debugging in the (Very) Large: Ten Years of Implementation and Experience

**Summary by:** GPT 6 Astra

**Author:** Kirk Glerum, Kinshuman Kinshumann, Steve Greenberg, Gabriel Aul, Vince Orgovan, Greg Nichols, David Grant, Gretchen Loihle, and Galen Hunt

**Source:** SOSP 2009; SIGOPS Hall of Fame Award 2019

**Link:** https://doi.org/10.1145/1629575.1629586

## Key insight

Large-scale error reporting needs counts for many failures but detailed state for only a selected subset. Grouping related reports and progressively collecting evidence turns a flood of crashes into a manageable debugging workload.

## Basic idea

Windows Error Reporting assigns reports to buckets [1], gathers diagnostic information progressively [2], and lets developers prioritize recurring failures. Initial labels use cheaply available crash information; server-side classification can refine those labels using symbols and richer reports. Statistics-based debugging [3] compares failure populations to identify conditions associated with a bug. Once a remedy is available, the service associates affected buckets with a response that can direct users to it.

## Illustrative example

**Report cheaply.** A document viewer crashes on several machines. A client submits a compact signature containing the relevant application and module versions, exception information, and failure location. The server records occurrences under an initial bucket without asking every client to upload its entire address space.

**Collect selectively.** The bucket is frequent but unexplained, so the service requests a diagnostic sample from selected occurrences. A minidump [4] provides stack and selected memory information. Server-side analysis with symbols shows that some initial labels correspond to the same function despite different executable layouts. Those reports can be grouped more usefully. Conversely, additional evidence can separate superficially similar crashes with distinct causes.

Suppose the minidump omits the corrupt object. Developers can configure further collection for relevant reports instead of enabling maximum collection for all failures. Collection policy must account for consent and sensitive data; reducing bandwidth alone does not establish that a report is safe to disclose.

**Use the population.** Imagine 180 of 200 reports in the refined bucket involve a particular add-in, but only 20 of 200 reports in a comparison population involve it. Those invented counts suggest a lead, not a proof that the add-in caused the crash: usage patterns, reporting selection, and version differences can confound the comparison. Developers investigate the code and diagnostic samples before attributing the defect.

**Close the loop.** A verified fix can be associated with the affected bucket so subsequent reporters receive an appropriate update recommendation. Counts also help measure whether the specific failure continues after deployment, subject to the reporting population and version information.

The mechanism does not require a perfect one-to-one mapping between bugs and buckets. Incorrect splitting wastes debugging effort; incorrect merging can conceal separate bugs. The paper treats classification as a practical, progressively refined approximation.

## Concepts and terms

**[1] Bucket.** A group of reports believed to arise from the same defect. Client-side labeling aims to avoid combining distinct defects; later classification can merge or otherwise refine groups using additional evidence.

**[2] Progressive collection.** Requesting more expensive diagnostic data only when the available information is insufficient. This separates the cost of counting occurrences from the cost of diagnosing representative failures.

**[3] Statistics-based debugging.** Using the distribution of errors and associated system properties to guide diagnosis. Correlation identifies candidates for investigation rather than establishing causation by itself.

**[4] Minidump.** A compact snapshot containing selected process state, such as stacks and limited memory, sufficient for some diagnoses but not every possible defect.
