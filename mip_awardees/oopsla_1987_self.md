# Self: The Power of Simplicity

**Summary by:** GPT 6 Astra

**Author:** David Ungar, Randall B. Smith

**Source:** OOPSLA 1987; SIGPLAN Most Influential OOPSLA Paper selection for 1986-1996 (retrospective award)

**Link:** https://doi.org/10.1145/38765.38828

**Code:** [Self](https://github.com/russellallen/self)

## Key insight

Objects can be created by copying other objects and share behavior through delegation, without a separate mandatory class mechanism.

## Basic idea

Self uses prototypes [1], named slots [2], and parent-based delegation [3]. A message can retrieve stored state or invoke behavior through the same lookup mechanism. Cloning creates an object's copy, while parent slots allow related objects to share methods. During an inherited method call, `self` [4] remains the original receiver, so shared behavior operates on that receiver's state.

## Illustrative example

**Prototype.** Construct a meter prototype with a writable `reading` slot initially zero and a parent slot pointing to a shared behavior object. The behavior object supplies `doubled`, a method that sends `reading` to self and multiplies the result by two. Assignment to the writable slot is exposed through its corresponding assignment message.

**Cloning.** Clone the meter twice to obtain `east` and `west`. Set east's reading to seven and west's to eleven. The copies have independent reading slots, while their parent references still point to the shared behavior object.

**Lookup.** Send `doubled` to east. East has no matching local method slot, so lookup finds the method through the parent. Its receiver is still east: the internal `reading` message returns seven and the result is fourteen. Sending the same message to west returns twenty-two, without copying the method implementation into both objects.

**Uniform access.** Another meter can answer `reading` with a method that computes a value rather than with a stored slot. The shared `doubled` method still sends the same message. This illustrates why clients need not distinguish state access from behavior invocation. Copying is not recursively duplicating every referenced object: shared parents and other referenced objects require deliberate treatment when defining an object's cloning behavior.

## Concepts and terms

**[1] Prototype.** An existing object used as the starting point for creating another by cloning, rather than by instantiating a separate class description.

**[2] Slot.** A named object component providing stored data, an assignment operation, or executable behavior.

**[3] Delegation.** Continue message lookup through designated parent objects when the receiver lacks a matching local slot.

**[4] Self.** The receiver of the current message; inherited methods retain that receiver rather than changing it to the object holding the method.
