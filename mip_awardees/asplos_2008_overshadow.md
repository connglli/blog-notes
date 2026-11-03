# Overshadow: A Virtualization-Based Approach to Retrofitting Protection in Commodity Operating Systems

**Summary by:** GPT 6 Astra

**Author:** Xiaoxin Chen, Tal Garfinkel, E. Christopher Lewis, Pratap Subrahmanyam, Carl A. Waldspurger, Dan Boneh, Jeffrey Dwoskin, Dan R. K. Ports

**Source:** ASPLOS 2008; ASPLOS Influential Paper Award 2026

**Link:** https://doi.org/10.1145/1353536.1346284

## Key insight

An operating system can manage an application's pages without being allowed to read their plaintext. A trusted virtual machine monitor can give the application and the guest kernel different views of the same memory and mediate transitions between them.

## Basic idea

Overshadow uses multi-shadowing [1] to select memory mappings according to the accessing context. Cloaking [2] exposes plaintext to the protected application and encrypted pages to the guest operating system. A protected shim [3] cooperates with the virtual machine monitor to preserve registers and adapt system calls across that boundary. Cryptographic metadata [4] checks page integrity and identity; availability, access-pattern leakage, and all malicious system-call behaviors are not covered by this protection claim.

## Illustrative example

**Protect a page.** An application keeps a private signing key in page `secret_page`. While application code runs, its shadow mappings expose the plaintext page. The guest kernel's normal mappings must not provide another plaintext alias.

**Let the kernel manage storage.** When the kernel needs to access the page for swapping, the monitor revokes its application mapping, encrypts the page, and records protected verification metadata. The kernel can move the ciphertext to storage without learning the signing key. The design can change a single physical page between views; it need not keep simultaneous plaintext and ciphertext copies of every page.

**Restore access.** Before the application can read the swapped-in page, the monitor checks the ciphertext against the protected metadata, decrypts it, and reinstates the application view. Modified ciphertext fails verification and causes termination rather than silently becoming application data. Associating metadata with the correct resource is necessary to detect substitution or replay, not just random corruption.

**Cross a system-call boundary.** A write request involving protected file data cannot simply hand its plaintext pointer to the kernel. The shim adapts the operation through protected mappings and the monitor. Other calls can require copying appropriate arguments through unprotected buffers. The monitor also protects saved registers and valid entry points when control moves between application and kernel.

**State what remains possible.** The kernel can refuse service or observe page-access timing. A vulnerable application may itself disclose its key. Those attacks do not contradict page cloaking's narrower confidentiality and integrity contract.

## Concepts and terms

**[1] Multi-shadowing.** The monitor selects different guest-physical-to-machine mappings for different execution contexts. This extends ordinary virtualization, which usually exposes one coherent guest physical view. Correctly recognizing the protected context is security-critical and cannot rely only on kernel-maintained identity information.

**[2] Cloaking.** Switch a protected page between application plaintext and external ciphertext views, revoking incompatible mappings during transitions. Encryption hides contents; verification detects unauthorized changes. The virtual machine monitor, its cryptography, and supporting trusted components remain part of the security boundary.

**[3] Shim.** Small application-side mediation code injected without rewriting the application's source. Together with the monitor it handles system calls, faults, interrupts, and protected thread contexts. Compatibility requires adapting interactions, not merely encrypting a process's heap.

**[4] Metadata and limitations.** Protected hashes, encryption information, and resource associations bind accepted ciphertext to the expected protected state. Protecting a page does not provide network encryption, a trusted keyboard/display path, or general protection against timing and memory-access side channels. The paper also leaves semantic attacks through portions of the system-call interface incompletely studied.
