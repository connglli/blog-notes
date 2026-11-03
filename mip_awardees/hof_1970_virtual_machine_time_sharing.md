# A virtual machine time-sharing system

**Summary by:** GPT 6 Astra

**Author:** R. A. Meyer and L. H. Seawright

**Source:** IBM Systems Journal 9(3), 1970; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1147/sj.93.0199

## Key insight

Sharing a computer need not require every user to run inside one common operating-system environment. A control program can present each user with a protected virtual copy of the machine and let that copy run its own operating system.

## Basic idea

CP-67 multiplexes an IBM System/360 Model 67 into virtual machines [1], each with apparent memory, processor state, devices, and an operator console. Ordinary instructions execute directly, while privileged operations [2] trap to the control program for simulation. Paging [3] translates each guest's memory into available physical storage, and I/O virtualization [4] translates device and buffer addresses. CMS [5] is a single-user interactive operating system suited to running in one such machine; different guests can also run different supported operating systems.

## Illustrative example

**Create two machines.** User Ada receives a virtual machine running CMS, while user Bo tests another supported System/360 operating system. Each guest has its own saved registers, program status, memory mapping, and virtual-device configuration. Both can use the same apparent low memory addresses without referring to the same private physical memory.

**Execute and intercept.** Ada's program adds two numbers using the real processor while her virtual machine is scheduled. When its guest operating system issues a privileged I/O instruction, the real processor is still executing guest code in problem state. Control passes to CP, which interprets the operation using Ada's virtual-machine state rather than granting the guest real supervisor authority.

**Translate I/O.** Suppose Ada reads from virtual disk D into a guest buffer. CP resolves D to its permitted real storage, translates the buffer's virtual addresses to physical addresses, and ensures the needed pages are resident. It constructs a corresponding channel-command sequence and starts the real operation. Completion is recorded in Ada's virtual status and reflected as an appropriate virtual interrupt when her machine resumes.

**Page and schedule.** An inactive guest page can reside on secondary storage. Accessing it causes CP to bring it into physical memory and update translation. While that transfer is pending, Bo's virtual machine can execute. If Bo's test operating system crashes, its own virtual state can be restarted without deliberately restarting Ada's guest.

**Compatibility boundary.** The paper excludes software requiring precise real-time instruction timing and problematic dynamically modified channel programs. CP translates channel programs rather than promising that every possible self-modifying device program behaves identically. Isolation also does not remove resource contention: many active virtual pages can overload paging even though their addresses remain protected.

## Concepts and terms

**[1] Virtual machine.** A software-maintained machine configuration and execution state presenting a guest with apparent processor, memory, console, and device resources.

**[2] Privileged operation.** An instruction requiring hardware supervisor authority. CP alone runs in real supervisor state; a guest's apparent supervisor mode is represented and simulated by CP.

**[3] Paging.** Mapping fixed-size virtual-memory units to physical memory and secondary storage. CP-67 uses 4096-byte pages and the Model 67's address-translation hardware.

**[4] I/O virtualization.** Mediating guest device requests, including translating both device identifiers and memory addresses and reflecting completion in virtual machine state.

**[5] CMS.** The Cambridge Monitor System described in this paper, an interactive operating system for a single machine user. Multiplexing many CMS instances is CP's responsibility rather than a separate multi-user policy inside each instance.
