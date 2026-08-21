# Overview

This blog takes notes of how to operate (version-control, build) the AOSP.

## Version-Control

AOSP is version-controlled as a [monorepo](https://en.wikipedia.org/wiki/Monorepo) by tool [repo](https://source.android.com/setup/develop/repo#init).

In a "monorepo", all relating projects, even though independent, are put in the same repository managed as a whole. In most sense, a monorepo is a single git repository like that of [Lerna](https://github.com/lerna/lerna). AOSP is not. Each project of AOSP is a single git repository and all these git repositories are managed as a whole by tool repo.

Each project managed by tool repo works like a git-submodule. To know which projects should be managed, tool repo tracks their address and corresponding revision in a manifest file. Under such version-control model, each project can be self-managed, and only the revision recorded in the manifest file is used (in this senes, repo also looks like a dependency management tool).

The manifest file itself is also managed as a git repository like [AOSP's platform/manifest repository](https://android.googlesource.com/platform/manifest/). We may name it the meta (or manifest) repository. Also, a manifest repository can have multiple manifest files.

#### Typiacal Workflow

1. Download the manifest repository by `repo init -u <url> -b <branch> -m <manifest>`, where `-u <url>` points to the manifest repository, `-b <branch>` tells which revision of the manifest repository should be used, and `-m <manifest>` defines the manifest file to use. After this step, the manifest repo is downloaded into `./.repo` directory. (This works like `git clone <url> -b <branch> .repo`.)
2. Sync (download) all projects by `repo sync -j <N>`. After this step, each project's manifest-defined revision is cloned into current directory (the manifest file also defines which path should be saved). Note that the `HEAD` of each project points to but detached from the corresponding revision defined in the manifest file. (This works like `foreach project's url/revision/path: git clone <url> -b <revision> <path>`.)
3. Start a new branch by `repo start <branch>`. After this step, all projects are created a new branch from the detached `HEAD`. (This work like `foreach project's path: cd path && git checkout -b <branch>`.)
4. Edit files. One can edit any file in the monorepo.
5. Save commits. Since each project is self-managed, one can use `git add` and `git commit` any times to save all changes locally. *NEVER USE `git push` to PUSH any local changes to remote.*
6. Upload local commits to reviewer server by `repo upload`. Once ready, local changes of each project are uploaded to reviewer server for review (not yet pushed).

#### Switch to existing branches

1. Update the manifest repository by `repo init -b <branch> -m <manifest>`. In this case, (if there's no updates of the manifest repository), `-u <url>` is not needed since the manifest repo is already downloaded. (This works like `cd .repo && git checkout <branch>` of the manifest repository)
2. Sync (checkout) all projects to the correct revision by `repo sync -j <N>`. Since other branch may have differenct revisions for some projects, this step download missed files, remove unused files, or update modified files. (This works like `foreach missed project's url/revision/path: git clone <url> -b <revision> <path>;`, `foreach existing project's path/revision: cd <path> && git checkout <revision>`, `foreach unused project's path: rm -rf <path>`.)
3. Start new branch, Edit, Save, and Upload like that in Typical Workflow.

> Note: NEVER use `repo forall -pc "git checkout <some-revision>"` to switch branches. Despite this works sometimes (when  some-revision is the single revision used in the manifest file), this breaks the repo model and may induce undefined repo  behaviors.

#### Other repo commands

Refer to [Repo Command Reference](https://source.android.com/setup/develop/repo), [Source Control Workflow](https://source.android.com/setup/create/coding-tasks), and `repo help`.

## Build AOSP

AOSP can be built inside a docker container using this Dockerfile. Refer to [`/platform/tools/docker`](https://android.googlesource.com/platform/build/+/refs/heads/master/tools/docker/) for a docker-container built.

Refer to [Buiding Android](https://source.android.com/setup/build/building) for building AOSP.

#### List of AOSP M Targets

The following is the main AOSP build commands:
+ `m`: build everything from the top directory.
+ `mm`: build everything in the current directory.
+ `mma`: build everything and their dependencies in the current directory.
+ `mmm <dir>`: build everything inside `<dir>`, e.g., `mmm art`.
+ `mmma <dir>`: build eveything and their dependencies inside `<dir>`, e.g., `mmma art`.

`m`-series commands combines the Make and Soong build system. So it is recommended to avoid using make or soong directly.

The following lists and explains some of AOSP m targets:
+ `m droid`: default target, build android frameworks and create all needed images (like ramdisk.img, system.img, vbmeta.img)
+ `m all`: builds everything that `m droid` does, plus everything that doesn't have the droid tag (e.g., developer tools). The build server runs this to make sure that everything that is in the tree and has an Android.mk file builds.
+ `m systemimage`: build the system image and dependent packages if there are changes.
+ `m snod`: quickly rebuild the system image from built packages (stands for "system no dependencies"). It does not build any packages, however, in practice, some of the builts (like right after `m build-art`) are not packed into the image ❓❓❓❓ .
+ `m vnod`: quickly rebuild the vendor image from built packages (stands for "vendor no dependencies").
+ `m pnod`: quickly rebuild the product from built packages (stands for "product no dependencies").
+ `m sdk sdk_repo`: create a system image and a repository xml file that can be used as a "system image update site" of Android Studio; refer to [Sharing AVD system images for others to use with Android Studio](https://source.android.com/setup/create/avd#sharing_avd_system_images_for_others_to_use_with_android_studio) for more information.
+ `m build-art`: quickly build a minimal host and target art.
+ `m build-art-host`: quickly build a minimal host art.
+ `m build-art-target`: quickly build a minimal target art.
+ `m test-art-host-run-test-dependencies`: build host art, host art's tests, and their dependencies
+ `m test-art-target-run-test-dependencies`: build target art, target art's tests, and their dependencies
+ `m idegen`: generate IDEA configurations that can help load AOSP into Intellij IDEA or Android Studio. See [here](https://stackoverflow.com/questions/16727607/can-we-use-android-studio-for-aosp-development) and [here](https://android.googlesource.com/platform/development/+/master/tools/idegen/README) for more information.
+ `m help`: show some common build targets.
+ Inspect the `Android.mk` and `Android.bp` of each project to check their specific build targets. Note, any Make targets (files or phony targets) and Soong module names are legitimate m targets.

#### References

+ https://source.android.com/setup/build/building
+ https://stackoverflow.com/questions/61769308/android-aosp-quickly-rebuild-system-img-only

## Build ART APEX

ART's apex can be built without the whole AOSP from Android S. Refer to the [`/platform/art/build`](https://android.googlesource.com/platform/art/+/refs/heads/master/build/) branch for documentation.

## Lunch Targets

In recent AOSP, the lunch target `aosp_x86_64-eng`, despite can be successfully built, fail to be started when typing `emulator [-no-window]` after building this target. `emulator` command complains the data partition image `userdata-qemu.img` is not generated. See the following error message.

``` sh
$ lunch aosp_x86_64-eng
$ m
$ emulator -no-window
...
qemu-system-x86_64-headless: Could not open '<path>/android/out/target/product/generic_x86_64/userdata-qemu.img': No such file or directory
```

[Here](https://www.reddit.com/r/androiddev/comments/odz9sp/building_aosp_error/) provides a solution for this issue: add `sdk_phone_x86_64-eng` targets to the lunch menu like the following:

``` diff
diff --git a/target/product/AndroidProducts.mk b/target/product/AndroidProducts.mk
index 7d9d90e..419cccb 100644
--- a/target/product/AndroidProducts.mk
+++ b/target/product/AndroidProducts.mk
@@ -84,3 +84,4 @@ COMMON_LUNCH_CHOICES := \
     aosp_arm-eng \
     aosp_x86_64-eng \
     aosp_x86-eng \
+    sdk_phone_x86_64-eng \
```

Then lunch `sdk_phone_x86_64-eng` instead of `aosp_x86_64-eng`.
