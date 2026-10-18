# Towards Removing Undef Values from LLVM IR

**Summary by:** DeepSeek V4.1 Flash and GPT 6 Astra

**Author:**

* Pedro Lobo (INESC-ID / Instituto Superior Técnico, University of Lisbon)
* John McIver (Virginia Tech), George Mitenkov (Aptos Labs), Juneyoung Lee (AWS), Kirshanthan Sundararajah (Virginia Tech), Nuno P. Lopes (INESC-ID / Instituto Superior Técnico, University of Lisbon)<br/>

**Source:** PLDI 2026 (Distinguished Paper Award)

**Link:** https://doi.org/10.1145/3808250<br/>

**Code:** [LLVM prototype](https://github.com/pedroclobo/llvm-project/tree/byte-type) and [Clang tests](https://github.com/jmciver/llvm-project/tree/users/jmciver/u2p-paper-clang-tests)

## Key insight

The last major use of `undef` in LLVM is the value of uninitialized memory. A raw byte type, whose bits carry per-bit poison and pointer provenance, together with a freezing load, is enough to replace that use with `poison`, paving the way for removing `undef` from LLVM IR at negligible performance cost.

## Basic idea

LLVM has two values for deferred undefined behavior [1]: `undef`, which may take a different value at every use (so `y * 2`, `y + y`, and `y << 1` are not all equivalent), and `poison`, which taints whole values and triggers UB when branched on, with `freeze` turning poison into a fixed non-deterministic value. Uninitialized memory remains a major source of `undef`, affecting bitfield encodings, raw copies, and comparisons. The paper changes uninitialized memory to `poison`, which needs two constructs: a raw byte type [2] that holds memory data in registers bit by bit, where each bit is an integer bit, a pointer bit with provenance [3], or poison, and a freezing load [5] that freezes the loaded bits before converting them to the requested type. A `bytecast` instruction [4] converts between bytes and other types; the byte representation makes `memcpy` lowering, `char` lowering, bitfield encodings, and load merging sound, because copying bytes preserves pointer provenance and keeps poison per bit. The paper implements the extension in LLVM 21 and Alive2 [9], upgrades old IR automatically [8], and measures an average run-time cost near zero after new optimizations, with the switch from `undef` to `poison` alone at net zero; 11 LLVM unit tests that Alive2 had flagged as unsound are fixed.

## Illustrative example: the first write to a bitfield

C and C++ bitfields share a word. This example follows one write, `s.a = 3`, to a struct whose memory is uninitialized:

```c
struct S { int a:3; int b:5; int c:24; };
void set_a(struct S *s) { s->a = 3; }
```

**Current encoding.** Clang reads and writes a bitfield by operating on the enclosing word [6]:

```
%w = load i32, ptr %s
%m = and i32 %w, -8      ; clear a's three bits
%v = or i32 %m, 3        ; set a = 3
store i32 %v, ptr %s
```

This is correct while uninitialized memory is `undef` [1]: the unwritten bits of `%w` are unconstrained, so clearing and setting a's three bits leaves b and c unconstrained.

**Why `poison` breaks it.** If uninitialized memory becomes `poison`, the load yields a poison value. Poison propagates through `and` and `or`, so `%v` is poison and the store poisons the whole word, including b and c. If b had been written earlier by a translation unit that used Clang's fine-grained one-byte bitfield encoding, its value is destroyed and the two encodings stop being compatible.

**The byte type and the freezing load.** With the byte type [2] and the freezing load [5], the write becomes:

```
%w = load i32, ptr %s, !freeze   ; load bytes, freeze per bit, bytecast to i32
%m = and i32 %w, -8
%v = or i32 %m, 3
store i32 %v, ptr %s
```

The freezing load reads the raw bytes, `freeze` replaces each poison bit with a stable non-deterministic bit, and `bytecast` [4] converts the result to `i32`. Bits that hold real data, such as b's bits after an earlier write, pass through unchanged, and only a's field is modified. Loading `i32` and freezing afterwards would not work: registers treat poison as value-wise, so one poison bit makes the whole word poison before the freeze, and freezing would then discard b's value.

**Raw copies.** The same byte representation fixes `memcpy`, which LLVM lowers to integer loads and stores. An integer copy can lose pointer provenance [3], making a later dereference invalid, and one poison bit taints all copied bytes. Copying bytes instead keeps provenance and poison per bit, so uninitialized data can become poison without breaking raw copies.

## Concepts and terms

**[1] undef, poison, and freeze.** LLVM's values for deferred UB. `undef` may yield a different value at every use, which is why `y * 2` and `y + y` are not equivalent when `y` is undef. `poison` is value-wise: most operations return poison when any operand is poison, branching on poison is immediate UB, and `freeze` converts poison into a fixed non-deterministic value that every use observes consistently. The paper's goal is to make uninitialized memory yield poison instead of undef. (The semantics come from [Taming Undefined Behavior in LLVM](freeze_and_poison.md).)

**[2] Byte type.** A register type `bW` that holds raw memory data as W bits. Each bit is an integer bit, a pointer bit `Ptr(p, i)` that records a pointer `p` and bit `i` of its address, or poison. This gives memory two properties that registers do not have: poison is per bit, and pointer provenance survives inside raw data. Memory is a map from block identifiers to blocks of bytes, pointers are (block, offset) pairs, allocations start as poison, and bytecasts generate no assembly.

**[3] Pointer provenance.** In the paper's model, pointers carry a block identifier as well as an offset; the identifier determines which allocation they may access. Explicit `ptrtoint` and `inttoptr` conversions can preserve access to an exposed allocation. Loading pointer bytes as an integer does not perform that explicit exposure, so an integer load/store copy can lose the provenance required for a later pointer dereference (Section 2.3).

**[4] bytecast.** An instruction converting between byte values and other types of the same bitwidth. The exact variant returns poison when a bit's kind does not match the target type; the type-punning variant returns poison only when some bit is poison and otherwise forces the conversion, mapping integer bits to a pointer without provenance (block 0). Values are converted to bytes with `bitcast`; `trunc`, `lshr`, `freeze`, `phi`, and `select` are extended to bytes. The paper also describes a simplified design with only the type-punning behavior, expressed through `bitcast` and type-punning loads.

**[5] Freezing load.** `load ty, ptr %p, !freeze` is shorthand for loading raw bytes, freezing them per bit, and converting the result to `ty`. It preserves bits that hold real values and turns poison bits into fixed non-deterministic bits. A plain `load ty` followed by `freeze` does not preserve real bits, because a single poison bit poisons the whole register value.

**[6] Bitfield lowering.** C and C++ bitfields pack several fields into one word. Clang reads a field by loading the word and shifting and masking; it writes a field by loading the word, clearing the field's bits, OR-ing in the new value, and storing the word. The first write reads uninitialized memory, which is why it needs a freezing load once uninitialized memory is poison. Clang also has a fine-grained encoding that accesses only the bytes containing a field; freezing loads keep the two encodings compatible.

**[7] Raw copies and load merging.** Lowering a raw copy to integer loads and stores can lose pointer provenance or spread poison. Merging adjacent integer loads can likewise let poison in one part contaminate another. Byte loads and stores preserve raw data; extracting each part of a merged byte load before converting it preserves the original poison boundaries.

**[8] IR auto-upgrade.** New LLVM versions read bitcode produced by older ones. The auto-upgrade rewrites old uses of undef to `freeze poison`, or to the zero constant where only a constant is allowed (global initializers), and rewrites loads to freezing loads. These are refinements of the old semantics: they may reduce nondeterminism but do not add behaviors.

**[9] Alive2.** A bounded translation validation tool integrated with LLVM. The authors extended it with the byte type, reusing its internal byte representation of memory and adjusting internal preprocessor optimizations that became unsound once byte-typed instructions are present. Validation time did not increase, 11 previously unsound unit tests (memcpy lowering and load widening) are fixed, and 330 reports on Draco are fixed; two new classes of reports appear, one from the known-unsound removal of `store undef` and one from Alive2's flow-insensitive tracking of escaped stack objects. Removing undef would also speed up validation, because reasoning about undef requires quantifier alternation.
