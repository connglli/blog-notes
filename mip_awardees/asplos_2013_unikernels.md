# Unikernels: Library Operating Systems for the Cloud

**Summary by:** GPT 6 Astra

**Author:** Anil Madhavapeddy, Richard Mortier, Charalampos Rotsos, David J. Scott, Balraj Singh, Thomas Gazagnaire, Steven Smith, Steven Hand, Jon Crowcroft

**Source:** ASPLOS 2013; ASPLOS Influential Paper Award 2025

**Link:** https://doi.org/10.1145/2451116.2451167

**Code:** [MirageOS](https://github.com/mirage/mirage)

## Key insight

Build a single-purpose virtual machine by linking the application with only the operating-system libraries it needs. A hypervisor supplies the stable hardware boundary, allowing whole-application specialization without maintaining drivers for every physical device.

## Basic idea

Mirage constructs unikernels [1] from application code and library-operating-system components [2]. Build-time configuration and specialization [3] select protocol stacks, storage interfaces, and other required services. The resulting image runs directly on a supported hypervisor interface, while type-safe code helps control interactions inside the image. Isolation between appliances comes from the hypervisor [4], not from separate protected processes inside each unikernel.

## Illustrative example

**Choose one service.** Build a small read-only HTTP service that serves an embedded status page. It needs network input, TCP, HTTP parsing, timing, and the page contents. It does not need an interactive shell, a package manager, or a general-purpose filesystem merely to return those bytes.

**Link the dependencies.** Express the service and its selected components as libraries. Configure the network backend for the target VM environment and compile them into one image. Static page contents and fixed configuration can be incorporated at build time, permitting unused functionality to be removed.

**Deploy.** Boot the image as a VM. A request moves through the linked network and HTTP code to the application, which returns the embedded page. There is no user-process-to-guest-kernel boundary between those library calls; the external virtualization boundary still separates this appliance from other tenants.

**Change the service.** Adding an endpoint may require rebuilding and redeploying the image. Dynamic parameters can still be supplied through application interfaces, but a setting compiled away is not an editable configuration file at runtime. If the appliance fails, its recovery unit is the service image rather than an independently restarted process inside a full guest distribution.

## Concepts and terms

**[1] Unikernel.** A specialized, single-purpose library-OS virtual machine image. It contains an application together with its required runtime and system services. It is not a container running atop an ordinary shared guest kernel.

**[2] Library operating system.** System facilities such as networking and scheduling are linked libraries rather than services reached through a conventional kernel system-call boundary. Mirage's use of OCaml provides type safety across much of this code. Low-level runtime and foreign-function components still require trust.

**[3] Specialization.** Move selected configuration decisions to build time and remove code or data that the particular appliance does not need. This can reduce image size, boot work, and exposed interfaces. It trades flexibility for specialization and does not prove that the remaining application logic is correct.

**[4] Isolation and threat model.** The hypervisor and control domain are trusted to separate VMs. Eliminating internal privilege boundaries avoids their costs but also removes them as protection between application and linked system components. A smaller attack surface is not immunity to protocol bugs, compiler defects, or malicious cloud infrastructure. The paper's results concern its Mirage prototypes and workloads, not a guarantee for every unikernel design.
