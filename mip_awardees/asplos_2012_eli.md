# ELI: Bare-Metal Performance for I/O Virtualization

**Summary by:** GPT 6 Astra

**Author:** Abel Gordon, Nadav Amit, Nadav Har'El, Muli Ben-Yehuda, Alex Landau, Assaf Schuster, Dan Tsafrir

**Source:** ASPLOS 2012; ASPLOS Influential Paper Award 2024

**Link:** https://doi.org/10.1145/2150976.2151020

## Key insight

Giving a virtual machine direct access to a device is not enough if every completion interrupt still visits the host. ELI lets assigned-device interrupts reach the guest directly while retaining host control over interrupts that do not belong to it.

## Basic idea

ELI builds on direct device assignment [1] and removes avoidable guest-to-host exits from interrupt delivery. A host-controlled shadow interrupt descriptor table [2] forwards guest-owned vectors directly and turns other vectors into intercepted exceptions. The host also permits the appropriate interrupt-completion operation [3] without an exit. Protected mappings and controlled handling of virtual interrupts [4] retain the virtualization boundary for an unmodified, untrusted guest.

## Illustrative example

**Assign a network device.** A VM runs on a mostly dedicated core and owns an assigned network-device function. Its guest kernel already has a handler for that device's completion interrupt. The host constructs a shadow table that points the assigned vector at that handler.

**Complete a packet.** The device raises its interrupt while the guest runs. Hardware consults the shadow table and invokes the guest handler without first exiting to the host. The guest consumes the completion and writes the allowed end-of-interrupt register directly. Removing exits from only delivery would leave overhead on this completion path.

**Keep a host interrupt.** A different vector belongs to the host. Its shadow-table entry is marked not present. Delivery generates a not-present exception configured to exit to the host, which identifies the original vector and invokes its own handler. A genuine guest not-present exception must instead be distinguished and reinjected appropriately.

**Inject a virtual event.** For an emulated device, the host temporarily enters an injection mode using the guest's original table and intercepted physical interrupts. It also traps the completion operation so the emulated interrupt is completed in the correct context. Once pending virtual interrupts are handled, normal exitless delivery resumes.

## Concepts and terms

**[1] Direct assignment.** A device or virtual hardware function belongs to a guest, allowing its ordinary I/O path to bypass host device emulation. Memory protection and device isolation still matter. Assignment alone does not remove interrupt-delivery and acknowledgment exits.

**[2] Shadow interrupt descriptor table.** The IDT maps interrupt vectors to handlers. ELI substitutes a protected, host-managed table while preserving the guest's view of its own table. Present guest-owned entries allow direct delivery; selected nonpresent entries trigger an exception that the host intercepts. The guest must not be able to rewrite these protected routing decisions.

**[3] End-of-interrupt access.** An interrupt controller needs notification that handling has completed. ELI selectively exposes the x2APIC EOI register rather than granting unrestricted access to all interrupt-controller state. Virtual-interrupt injection requires different trapping behavior.

**[4] Scope and isolation.** ELI coordinates table mappings, guest configuration changes, interrupt affinity, and nested interrupts. Its performance design assumes mostly dedicated physical cores for virtual CPUs; heavy multiplexing introduces additional transitions. Near-bare-metal results are measurements for the paper's workloads and configuration, not a promise that every virtualized workload becomes free of overhead.
