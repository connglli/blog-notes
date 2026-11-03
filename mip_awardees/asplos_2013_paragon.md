# Paragon: QoS-Aware Scheduling for Heterogeneous Datacenters

**Summary by:** GPT 6 Astra

**Author:** Christina Delimitrou, Christos Kozyrakis

**Source:** ASPLOS 2013; ASPLOS Influential Paper Award 2024

**Link:** https://doi.org/10.1145/2451116.2451125

## Key insight

A small amount of profiling can become useful scheduling information when combined with measurements of related workloads. Predict both which hardware suits an application and which colocated applications it can tolerate.

## Basic idea

Paragon profiles a new workload briefly and uses collaborative filtering [1] to estimate its performance across server configurations [2]. It also estimates interference caused and tolerated [3] for several shared resources. A greedy scheduler [4] first filters placements that are predicted to violate performance requirements, then chooses a suitable hardware configuration and close-fitting colocation. These are learned performance predictions, not unconditional quality-of-service guarantees.

## Illustrative example

**Predict behavior.** A new service has measurements on two machine types. Similarities to previously profiled workloads fill in estimated performance on other configurations. Controlled interference measurements and the same reconstruction approach estimate how much cache contention the service causes and tolerates.

**Check both directions.** For a toy normalized cache-interference scale, suppose the service causes `0.4` and tolerates `0.7`. A fast machine's existing load causes `0.8` and tolerates `0.9`. The service would fit the existing load's tolerance, but the existing load exceeds the service's tolerance: `0.7 - 0.8 < 0`. The scheduler rejects this placement despite its attractive processor.

**Choose a compatible machine.** Another machine's load causes `0.2` and tolerates `0.5`. Its two margins are `0.5 - 0.4 = 0.1` and `0.7 - 0.2 = 0.5`, both nonnegative. Assuming the other modeled resources are also compatible, it survives filtering. The scheduler then considers hardware preference and packing among the surviving machines. The numbers illustrate the decision rule, not measured application scores.

**Update the model.** As applications arrive, finish, or change behavior, server-state summaries and workload observations must be updated. A wrong classification or a phase change can invalidate a prediction, so monitoring and adaptation remain necessary.

## Concepts and terms

**[1] Collaborative filtering.** Represent known performance observations in matrices with workloads as rows and configurations or interference conditions as columns. Low-dimensional factors capture shared behavior; reconstruction estimates missing entries using measured data. Paragon combines singular-value decomposition and latent-factor reconstruction rather than fully profiling each new workload in every environment.

**[2] Heterogeneity.** Machines differ in processor, memory, and other resources, so the fastest configuration depends on the workload. A partial performance profile predicts a ranking of configurations rather than assuming all machines provide interchangeable capacity.

**[3] Caused and tolerated interference.** For each modeled resource, distinguish the pressure an application creates from the pressure it can withstand at its performance target. Paragon summarizes a server's caused interference by adding resident-workload scores and its tolerance by taking their minimum. These summaries are models of colocation, not physical conservation laws.

**[4] Greedy placement.** Require nonnegative margins in both directions for the considered interference sources. Among survivors, prefer the best predicted server configuration, then minimize excess margins to avoid unnecessarily loose packing. The decision uses current information and does not optimize an unknown future workload sequence. Its effectiveness depends on representative training data and useful interference models.
