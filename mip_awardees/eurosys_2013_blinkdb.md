# BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data

**Summary by:** GPT 6 Astra

**Author:** Sameer Agarwal, Barzan Mozafari, Aurojit Panda, Henry Milner, Samuel Madden, Ion Stoica

**Source:** EuroSys 2013; EuroSys Test-of-Time Award 2023

**Link:** https://doi.org/10.1145/2465351.2465355

## Key insight

Choose which data to sample before queries arrive, but choose how much of a sample to read after seeing the query's accuracy or latency requirement. Sampling by recurring combinations of columns keeps rare groups visible without predicting every future predicate value.

## Basic idea

BlinkDB answers supported aggregate queries [1] using stored samples rather than always scanning the original table. It chooses multidimensional stratified samples [2] from historical query column sets [3] and a storage budget. At query time, small trial executions build an error-latency profile [4] that guides sample selection and size. Weighted aggregation [5] corrects unequal sampling rates, while reported confidence intervals distinguish an approximate answer from an exact result.

## Illustrative example

**Prepare samples.** A table contains 1,000 purchases: 900 from a large shop and 100 from a small shop. Queries often filter or group by `shop`, so consider a sample stratified on that column. In this illustrative configuration, keep 100 randomly chosen rows from the large shop and all 100 rows from the small shop. The inclusion rates are `1/9` and `1`, respectively.

**Answer a filtered query.** A user asks for the small shop's average purchase value. A uniform sample of the same total size would contain relatively few small-shop rows, while this stratified sample contains its complete group. The exact predicate value need not have appeared in an earlier query; the recurring column set is what guided sample construction.

**Correct unequal rates.** For an approximate count of purchases satisfying an additional predicate, a matching sampled row from the large shop represents nine population rows, while one from the small shop represents one. If the sample contains 12 and 7 matching rows, respectively, the estimated count is `12*9 + 7 = 115`. Simply counting 19 or multiplying both groups by the same factor would be wrong. The estimate still has sampling uncertainty because the large group was sampled.

**Choose the work.** For a tighter accuracy requirement, BlinkDB probes small sample subsets, estimates variance and selectivity, then reads enough rows to meet its estimated error target. For a time budget, it estimates processing rate and chooses how many rows it can examine. If a useful sample does not contain enough information, a small sample cannot manufacture a precise answer.

## Concepts and terms

**[1] Aggregate query.** A query summarizes rows, for example with counts, sums, averages, or quantiles, possibly after filtering or grouping. The paper does not provide a general approximate implementation of arbitrary SQL joins and nested queries; it supports selected join cases involving small dimension tables.

**[2] Stratified sample.** Divide rows into groups according to values of selected columns, then sample within each group. Retaining small groups more heavily protects rare values. BlinkDB chooses a set of samples under a storage budget and can use different sample sizes during execution.

**[3] Query column set.** The columns used for filtering and grouping, abstracting away specific constants. Historical frequencies guide sample construction. This is a workload assumption about recurring structure, not knowledge of all future queries.

**[4] Error-latency profile.** Small executions estimate how error decreases and running time grows with additional sampled rows. The latency prediction depends on available resources and data placement; it is not a hard real-time guarantee under arbitrary interference.

**[5] Weighting and confidence.** Unequal inclusion probabilities require corresponding statistical weights. Confidence intervals depend on the sampling design and estimator assumptions; a stated confidence level does not promise that every individual query is within its interval. Reusing samples can also correlate errors across queries.
