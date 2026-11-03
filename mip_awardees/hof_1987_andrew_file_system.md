# Scale and Performance in a Distributed File System

**Summary by:** GPT 6 Astra

**Author:** John H. Howard, Michael L. Kazar, Sherri G. Menees, David A. Nichols, M. Satyanarayanan, Robert N. Sidebotham, and Michael J. West

**Source:** SOSP 1987; full paper in ACM Transactions on Computer Systems 6(1), 1988; SIGOPS Hall of Fame Award 2008

**Link:** https://doi.org/10.1145/35037.35059

## Key insight

Server work scales better when ordinary reads are satisfied by clients and cached validity is protected by callbacks. Whole-file caching, client-side pathname traversal, and volume-level administration reinforce that division of work.

## Basic idea

Andrew's Venus cache manager [1] stores whole files on a workstation and contacts Vice servers mainly for opens, closes, and metadata operations. A callback [2] lets Venus trust cached data until the server revokes its promise, reducing repeated validation traffic. Cached directories support local name translation, while stable file identifiers [3] avoid sending full pathnames for every access. Files are grouped into volumes [4] for location and administration. The resulting consistency is based on opens and closes, not instantaneous visibility of every write across all clients.

## Illustrative example

**Open locally.** Workstation A opens `/team/report`. Venus walks cached directories and finds a cached file whose callback remains valid. No server interaction is required for this open in the ordinary failure-free case. Reads then operate on the local copy without sending each byte request to Vice.

**Modify and close.** A edits the file. Other processes on A can see local writes according to the workstation's normal behavior, but workstation B does not see those changes while A's file remains open. On close, Venus sends the modified contents to the appropriate server. The server invalidates relevant callback promises so later opens obtain the new version.

**Distinguish open instances.** B opens the file after A's successful close and sees the updated contents. If B had opened it before that close, its already-open instance need not change underneath it. This open/close rule is the intended contract, not a cache bug to be disguised as full single-machine write visibility.

Concurrent writers require application cooperation. The system does not implicitly lock every open file to serialize arbitrary updates from different workstations; applications needing that property must arrange synchronization.

**Locate a moved collection.** The file identifier contains a volume identifier, an object number, and a uniqueness component. A volume-location lookup identifies the responsible server without changing the file's identity or every pathname referring to it. Aggregating location information by volume avoids maintaining a separate global location entry for every file.

**Recover cache confidence.** After workstation restart, cached bytes still on disk are not automatically current. Venus treats callbacks as suspect and validates entries on first use. Server and network failures also require callback-state recovery; persistent cached data is not equivalent to a persistent validity promise.

## Concepts and terms

**[1] Venus and Vice.** Venus is the workstation-side cache manager; Vice is the shared server system. Local caching keeps frequent data access off the server path.

**[2] Callback.** A server promise to notify a caching workstation before permitting conflicting modification. It replaces repeated polling with maintained server/client state that must be repaired after failures.

**[3] File identifier.** A location-independent identifier comprising a volume, an object within that volume, and a uniqueness value distinguishing reused object numbers. It is separate from a pathname.

**[4] Volume.** A collection of files forming an administrative and location unit. Volumes support operations such as movement and read-only replication without requiring per-file location management at every client.
