# Arrakis: The Operating System is the Control Plane

**Summary by:** GPT 6 Astra

**Author:** Simon Peter, Jialin Li, Irene Zhang, Dan R. K. Ports, Doug Woos, Arvind Krishnamurthy, Thomas Anderson, and Timothy Roscoe

**Source:** OSDI 2014; SIGOPS Hall of Fame Award 2026

**Link:** https://www.usenix.org/conference/osdi14/technical-sessions/presentation/peter

**Code:** [Arrakis source](https://github.com/UWNetworksLab/arrakis)

## Key insight

The kernel can authorize and configure device access without mediating each subsequent I/O operation. Protected virtual device interfaces let application libraries handle the frequent data path while hardware enforces the configured resource boundaries.

## Basic idea

Arrakis moves ordinary network and storage processing into application-level libraries [1], leaving resource allocation, naming, and authorization in the kernel control plane. Each application receives virtual device interfaces [2] with its own queues. Privileged network filters [3], virtual storage areas [4], and DMA isolation [5] constrain what those queues can access. The libraries then submit operations directly, using either a compatibility interface or a more specialized API. The architecture requires suitable device support; its prototype emulates missing storage-virtualization features rather than assuming every evaluated device already implements the complete hardware model.

## Illustrative example

**Authorize a service.** Consider a read-only object server under the paper's device model. The control plane assigns it a virtual network interface accepting requests for its service address, plus a virtual storage interface exposing a 128-block area backed by physical blocks beginning at 1000. It also configures which memory buffers the devices may access. The application cannot change these permissions by writing a queue entry.

**Receive directly.** A request asks for the object in virtual block 7. A receive filter directs its packet to the service's queue, and the network device transfers it into an authorized application buffer. The service's library handles protocol processing and exposes the request to application code without entering the kernel for every packet.

**Read storage.** The storage library submits a one-block read at virtual offset 7. The virtual controller checks that the transfer fits the assigned area and translates it to physical block 1007. A request extending beyond block 127 must fail the area's bounds check. DMA isolation separately prevents a valid disk request from targeting another application's memory; storage bounds alone would not provide that protection.

**Reply and manage.** After completion, the library prepares a response and places it on the network transmit queue. Its configured transmit filter permits the service's authorized identity and destinations, rather than trusting an arbitrary header supplied by application code. Allocating another storage area, changing filters, or configuring rate limits requires returning to the control plane.

**Distinguish the prototype.** The paper's available network hardware supports only parts of the desired filtering model. For storage, a dedicated processor core emulates virtual controllers by checking requests, translating storage and memory addresses, and forwarding them to the physical controller. The storage evaluation does not assume that the complete virtualization model already exists in hardware.

Direct access does not establish an application's crash consistency or eliminate device contention. A writable service still needs a correct persistence protocol, and a compromised library can corrupt resources within its own authorized area.

## Concepts and terms

**[1] Application-level I/O library.** Protocol and storage code running inside the application protection domain. It can specialize its own data structures without multiplexing unrelated applications through every operation.

**[2] Virtual device interface.** An independently accessible set of device registers and queues, mapped to one authorized protection domain while the physical device remains shared.

**[3] Network filter.** A privileged packet-header predicate controlling permitted transmissions or routing received packets to a queue. Filtering provides demultiplexing and access policy, not complete TCP processing in the device.

**[4] Virtual storage area.** A persistent region mapped to physical storage extents. Applications use offsets within it; the controller enforces the region boundary and performs the translation.

**[5] DMA isolation.** Direct memory access lets devices transfer data without CPU copying. Isolation restricts accessible buffers through an I/O memory-management unit, or through software checks in the prototype.
