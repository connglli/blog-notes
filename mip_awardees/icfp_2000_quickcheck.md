# QuickCheck: A lightweight tool for random testing of Haskell programs

**Summary by:** GPT 6 Astra

**Author:** Koen Claessen and John Hughes

**Source:** ICFP 2000; SIGPLAN Most Influential ICFP Paper Award 2010.

**Link:** https://doi.org/10.1145/351240.351266

**Code:** [QuickCheck library project](https://github.com/nick8325/quickcheck)

**Documentation:** [QuickCheck library documentation](https://hackage.haskell.org/package/QuickCheck/docs/Test-QuickCheck.html)

## Key insight

Write general executable properties, then generate many inputs to search for counterexamples. The input distribution is part of the test's design, not an incidental implementation detail.

## Basic idea

QuickCheck represents properties [1] as Haskell functions and runs them on generated inputs. Type-directed generators [2] supply ordinary values, while custom generators use combinators and size parameters [3] to produce application-specific data. Conditional properties [4] discard cases outside their preconditions, and classification reports help reveal uninformative test distributions. Passing tests is evidence about sampled cases, not a proof that the property holds for all inputs.

## Illustrative example

**Property.** A list-rotation routine should preserve list length. A second useful property says that rotating a nonempty list by its length gives back the same list. These are different obligations: a function returning the input unchanged satisfies both, so they do not completely specify rotation.

Here is a simple implementation and one executable property:

```haskell
rotate :: Int -> [a] -> [a]
rotate _ [] = []
rotate n xs = drop k xs ++ take k xs
  where k = mod n (length xs)

prop_length :: Int -> [Int] -> Bool
prop_length n xs = length (rotate n xs) == length xs
```

**Generation.** A generator produces integers for `n` and lists whose lengths and elements depend on a size bound. For `n = 2` and `xs = [7,4,9]`, the implementation returns `[9,7,4]`, so the property holds.

Suppose a faulty implementation uses `take (k+1)` instead of `take k`. The same input returns `[9,7,4,9]` and falsifies the length property. The reported input is a concrete debugging case.

**Distribution.** If tests overwhelmingly use empty lists, this bug can remain hidden. Classify generated cases by empty, singleton, and longer lists, and inspect their frequencies. A property restricted to nonempty lists can reject empty cases, but a rare precondition may waste most attempts. A generator that directly constructs the required shape is often more informative.

The 2000 paper's mechanism is random property checking with controllable generation and reporting. Automatic counterexample shrinking, familiar from later QuickCheck systems, is not needed to explain this paper and should not be assumed as part of this example.

## Concepts and terms

**[1] Property.** An executable statement expected to hold for every input in its domain. A failed evaluation supplies a counterexample; a finite successful test run does not establish universal validity.

**[2] Type-directed generator.** A generator selected through the `Arbitrary` type-class interface. Instances define how to create values of a type and can be overridden or specialized.

**[3] Size parameter.** A bound or scale controlling generated structures. Recursive generators must reduce or divide their size allowance so generation itself does not grow without control.

**[4] Conditional property.** A property with a precondition; inputs violating it are discarded rather than counted as successful evidence for the consequent.

