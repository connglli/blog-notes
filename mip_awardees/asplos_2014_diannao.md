# DianNao: A Small-Footprint High-Throughput Accelerator for Ubiquitous Machine-Learning

**Summary by:** GPT 6 Astra

**Author:** Tianshi Chen, Zidong Du, Ninghui Sun, Jia Wang, Chengyong Wu, Yunji Chen, Olivier Temam

**Source:** ASPLOS 2014; ASPLOS Influential Paper Award 2024

**Link:** https://doi.org/10.1145/2541940.2541967

## Key insight

Fast neural-network arithmetic is insufficient if fetching weights and activations dominates cost. DianNao combines a compact computation pipeline with explicitly managed storage and tiled execution so that useful data reuse happens close to the arithmetic.

## Basic idea

DianNao executes neural-network layers in tiles [1] rather than building hardware for every neuron in the model. Its neural functional unit [2] performs products, reductions, and activation or pooling operations. Separate input, output, and weight buffers [3] feed the unit and exploit the different access patterns of those values. Fixed-point arithmetic [4] reduces hardware cost, but its numerical behavior is not identical to floating-point execution.

## Illustrative example

**Define a layer.** Two output neurons consume the input `[1, 2, 3, 4]`. Their weight rows are `[2, 1, 0, 1]` and `[1, 0, 1, 0]`; omit biases. The unactivated outputs should be 8 and 4. Use an illustrative tile containing two inputs and both outputs, smaller than the paper's hardware configuration.

**Feed a tile.** Put the first two inputs into the input buffer and the corresponding weights into the synapse buffer. Multiplication produces `[2, 2]` for the first neuron and `[1, 0]` for the second. The reduction stage obtains partial sums 4 and 1. The same input values serve both output neurons.

**Accumulate.** Load the remaining inputs and weights, producing additional sums 4 and 3. Accumulate them with the existing partial sums to obtain 8 and 4. Applying a nonlinear activation to each partial sum would generally be wrong; activation waits until all input tiles for that output have contributed.

**Finish and reuse storage.** The activation stage transforms the completed sums and writes results to the output buffer. Controller commands sequence transfers and computations, allowing the compact unit to process a larger layer through repeated tiles. The weights need not all fit on chip, but transfers from external memory still consume bandwidth and energy.

## Concepts and terms

**[1] Tiling.** Split a larger layer into groups of input values and output neurons that fit the accelerator's working storage. Keep or reuse values while processing the associated tile, then move to the next. Convolution changes which input windows and shared weights participate; pooling requires reductions without the same multiplication stage.

**[2] Neural functional unit.** A staged datapath containing parallel multipliers, reduction operators, and activation support. The reduction stage accumulates contributions across input tiles, so the activation stage does not necessarily run for every earlier-stage cycle. The paper implements nonlinear functions using piecewise-linear approximation.

**[3] Split buffers.** `NBin` stores input neurons, `NBout` stores output neurons, and `SB` stores synaptic weights. Dedicated structures match different transfer widths and avoid general-purpose cache tag checks and conflicts. Accumulation registers retain intermediate sums. Data movement and buffer scheduling are central to the design, not incidental implementation details.

**[4] Fixed-point representation.** Values use a fixed division between integer and fractional bits rather than a floating exponent. The paper uses 16-bit arithmetic and evaluates its accuracy tradeoff on selected networks and datasets. Rounding, truncation, range limits, and activation approximation remain relevant; the reported small accuracy differences do not establish lossless conversion for arbitrary models or training algorithms.
