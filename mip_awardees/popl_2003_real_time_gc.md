# A real-time garbage collector with low overhead and consistent utilization

**Summary by:** GPT 6 Astra

**Author:** David F. Bacon, Perry Cheng, and V. T. Rajan

**Source:** POPL 2003; SIGPLAN Most Influential POPL Paper Award 2013.

**Link:** https://doi.org/10.1145/604131.604155

**Code:** [Jikes RVM research runtime](https://github.com/JikesRVM/JikesRVM)

## Key insight

Bounding individual collection pauses is insufficient if pauses can occur almost back to back. A real-time collector also needs a predictable share of processor time for the application and bounded work for every collection operation.

## Basic idea

The collector interleaves application execution, called mutation [1], with small collection quanta using time-based scheduling [2]. Incremental mark-sweep [3] handles ordinary reclamation, while selective copying repairs fragmentation. Forwarding pointers and read barriers [4] preserve access to moved objects, and arraylets [5] divide large arrays into bounded pieces. These mechanisms support predictable utilization only with suitable bounds on allocation, live memory, and available collection throughput.

## Illustrative example

**Schedule.** Consider an illustrative schedule with 3 milliseconds of application execution followed by 2 milliseconds of collection, repeated while collection is active. Ignore scheduling and barrier overhead in these toy numbers. Every full 5-millisecond interval contains 3 milliseconds of application time, so its utilization is 60 percent. A 1-millisecond interval wholly inside a collector quantum has zero application utilization: the interval length matters.

If collection were triggered solely after every fixed number of allocated bytes, an allocation burst could instead cause a burst of pauses. Dividing work into small units would bound each pause without guaranteeing useful application time between them.

**Heap work.** Suppose one allocation page contains a single surviving small object and another compatible page has room for it. Moving that object can release the sparse page for reuse. The old location receives forwarding information. A mutator reference to it is redirected to the current copy; incremental tracing also updates references so obsolete copies can eventually be reclaimed.

A large array cannot be copied or scanned as one uninterruptible task. Split it into fixed-size arraylets and process a bounded piece before checking whether the collection quantum has expired. The application's logical indexing operation selects the appropriate piece and offset.

**Capacity condition.** The collector needs enough reserved CPU time and spare memory to finish before allocation consumes the available space. The example schedule alone does not establish that condition. A system that allocates faster than its configured collection budget can sustain does not obtain an unconditional real-time memory guarantee.

## Concepts and terms

**[1] Mutator.** Application code that allocates objects and changes references. Mutator utilization over an interval is the fraction of that interval available to the application; minimum utilization considers the worst interval of that length.

**[2] Time-based scheduling.** Alternating application and collector quanta according to elapsed time rather than only allocated bytes. Collector operations must be interruptible at a fine enough granularity.

**[3] Incremental mark-sweep.** Finding reachable objects and reclaiming unreachable ones in interleaved steps. This collector uses snapshot-at-the-beginning marking with barriers that preserve the relevant reachability information during mutation.

**[4] Read barrier.** Code on reference access that redirects a reference when its object has moved. The collector uses object-header forwarding information to keep mutator accesses consistent during relocation.

**[5] Arraylet.** A bounded-size piece of a logical array. Splitting arrays limits individual scan and copy work and reduces allocation difficulties caused by large contiguous objects.

