# JFlow: Practical mostly-static information flow control

**Summary by:** GPT 6 Astra

**Author:** Andrew C. Myers

**Source:** POPL 1999; SIGPLAN Most Influential POPL Paper Award 2009.

**Link:** https://doi.org/10.1145/292540.292561

**Documentation:** [Jif, the successor to JFlow](https://www.cs.cornell.edu/jif/)

## Key insight

A type checker can track who may learn a value, including information revealed by control flow. Decentralized labels let different owners impose their own policies and relax only policies they are authorized to control.

## Basic idea

JFlow extends Java types with information-flow labels [1]. Assignments must respect the ordering of these labels, and the program-counter label [2] tracks information learned by reaching a statement. A decentralized label [3] combines policies belonging to separate owners; declassification [4] can relax an owner's policy only with appropriate authority. Inference and polymorphism reduce annotation requirements, while runtime label tests handle cases whose policies are not statically known.

## Illustrative example

**Setup.** A service holds a private Boolean `approved`. Its label has one policy: owner `Clinic` permits readers `Clinic` and `Doctor`. A public output channel has no confidentiality restriction. A doctor's channel accepts information protected by the clinic's policy.

Consider a branch that writes 1 to an output when `approved` is true and 0 otherwise. Although the written constants are public, the selected value reveals the private bit.

**Checking the branch.** Evaluating the test raises the program-counter label to include the label of `approved`. Each assignment must accommodate both the value's label and this control-flow label. Writing either constant to the public channel therefore fails the information-flow check. Writing it to the authorized doctor's channel is allowed.

If a second owner, `ResearchGroup`, also labels the value with readers `ResearchGroup` and `Analyst`, both policies apply. A recipient must be permitted by each owner's policy; policies are not combined by taking the union of all reader names.

**Controlled release.** Code acting with `Clinic`'s authority can explicitly relax the clinic's policy when the application intends a release. It cannot thereby remove the research group's independent policy. The checker verifies authority and permitted label changes, not whether a human organization's decision to release this particular fact is wise.

A rough checker attaches labels to expressions, joins labels at combinations of information, extends the control-flow label inside branches, and generates ordering constraints at assignments and calls. Runtime-dependent policies require the language's checked label operations rather than unchecked casts.

## Concepts and terms

**[1] Information-flow label.** A confidentiality restriction associated with data. Flow is allowed toward a destination at least as restrictive as the source, not merely because both have the same ordinary Java type.

**[2] Program-counter label.** A summary of the information revealed by the current control path. It prevents implicit leaks through which statements execute, even when their assigned expressions are constants.

**[3] Decentralized label.** A collection of owner-reader policies. Each owner retains control of its policy, and permitted observations must satisfy all applicable policies.

**[4] Declassification.** An explicit relaxation of confidentiality checked against the authority held by the executing code. It is a controlled exception to ordinary flow restrictions, not an automatic inference that data is harmless.

