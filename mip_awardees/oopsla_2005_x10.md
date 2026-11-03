# X10: An Object-Oriented Approach to Non-Uniform Cluster Computing

**Summary by:** GPT 6 Astra

**Author:** Philippe Charles, Christian Grothoff, Vijay Saraswat, Christopher Donawa, Allan Kielstra, Kemal Ebcioglu, Christoph von Praun, Vivek Sarkar

**Source:** OOPSLA 2005; SIGPLAN Most Influential OOPSLA Paper Award, 2015

**Link:** https://doi.org/10.1145/1094811.1094852

**Code:** [X10](https://github.com/x10-lang/x10)

## Key insight

Expose where mutable data lives and make remote work explicit, while providing structured completion for activities that can spawn further activities.

## Basic idea

X10 organizes computation and mutable storage into places [1] within a partitioned global address space [2]. Asynchronous activities [3] can be started at chosen places, and `finish` [4] waits for work spawned transitively within its scope. Local atomic blocks [5] protect compound updates shared by activities. Knowing a remote reference does not authorize a direct local access to its mutable fields.

## Illustrative example

**Placement.** Put the first half of an immutable input at place P and the second half at place Q. Keep a mutable result accumulator at P, initially zero. A parent activity at P enters a `finish` scope and starts one activity for each half, each at the place where its data is accessible.

**Local computation.** The P activity sums values two and three, obtaining five. The Q activity sums seven and eleven, obtaining eighteen. To contribute eighteen, Q starts another asynchronous activity at P; it does not directly mutate P's accumulator from Q.

**Atomic contribution.** Each contributing activity at P performs the accumulator's read-add-write in an atomic block. Otherwise two activities could both read zero and overwrite one another, losing a contribution. The blocks serialize these local updates; they do not create a transaction spanning arbitrary remote places.

**Completion.** The activity at Q may finish after launching its contribution, before that contribution has run. The outer `finish` still waits for the descendant activity at P. When the scope completes normally, the accumulator is twenty-three and the parent can use it. A synchronization scheme that waited only for the two direct children could read five too early. The example assumes no exceptions; X10's finish construct also serves as a collection point for exceptions from the enclosed activity tree.

## Concepts and terms

**[1] Place.** A locality domain associated with activities and mutable storage.

**[2] Partitioned global address space.** Objects can be globally named, but access and locality rules distinguish where their mutable state resides.

**[3] Asynchronous activity.** Independently scheduled work whose creation returns without waiting for its completion.

**[4] Finish.** A construct waiting for the enclosed statement and its transitively spawned activities to complete.

**[5] Atomic block.** A local compound action executed indivisibly with respect to competing local activities, subject to restrictions on its contents.
