# Building and releasing AyuGram

The application keeps AyuGram's name, icons, feature defaults and platform
identifiers. Repository ownership is not application branding. A development
fork must identify where its binaries come from; it must not claim to be an
official upstream release.

## Build checks

`Source checks` runs on pushes and pull requests without production
credentials. It runs the unit tests in `Telegram/build`, checks that
`prepare.py` still parses, and lints the workflows with `actionlint`. It does
not compile the C++ application.

`Release` runs only by an explicit manual dispatch, and only from the default
branch. It validates the version and the credentials before starting the
expensive jobs, then builds universal macOS and Windows x64 packages plus the
full recursive source archive. Each macOS architecture builds in its own job
because one cold build of both exceeds the six-hour job limit. The workflow
creates the tag and public GitHub Release only after every build and package
check succeeds. A version that is already tagged still builds; only the
publishing step is skipped, so the pipeline can be exercised without
republishing and a release that failed after tagging can be retried.

Both platform jobs report into the log and the run summary: time per CMake
target and the slowest translation units from `.ninja_log`, compiler cache
statistics, the processor count, and on macOS the swap used during
compilation. Read that report, not a stopwatch, when a build gets slower. A
compiler cache hit rate near zero explains an otherwise inexplicable
three-hour job, and swap above a few hundred megabytes means three parallel
compilers do not fit in the runner's memory.

## Releasing a new Telegram version

1. Branch from the default branch and merge the upstream tag:
   `git switch -c codex/ayu-<version> origin/dev --no-track`. Resolve the
   conflicts in the AyuGram-patched sources. If upstream moved the `lib_ui` or
   `lib_tl` pins, merge and push those repositories first.
2. Set the version in `Telegram/build/version`. It is the only place the
   version is written; the workflow reads it and requires the branch to be
   named `codex/ayu-<version>`.
3. Push the branch and let `Source checks` go green before anything expensive
   starts.
4. Dispatch the release **from the default branch**, naming the branch to
   build:
   `gh workflow run Release --ref dev -f ref=codex/ayu-<version>`.

Step 4 is not a convenience. A run reaches only the caches of its own ref and
of the default branch, and the release branch is renamed every version, so a
release dispatched on its own branch would write caches nothing else can ever
read and start cold every time. The workflow refuses to run anywhere but the
default branch for that reason. Which branch is the default must not change
again: it moved at 7.2.5, which scoped every cache to a branch that was no
longer the default and left the next release cold. Moving the `dev` tip is a
different thing and is fine, because caches are scoped to the ref name.

How long the dependency half takes depends on what upstream shipped, and the
gap is wide enough to plan around. The macOS dependency cache key hashes
`Telegram/build/prepare/**` and `Telegram/build/qt_version.py`, the Windows
one hashes `prepare.py` and the SDK version. Neither changed across the six
version bumps from 7.1.4 to 7.2.5, so all of them reused a dependency tree
that costs an hour or two per platform to build, and the last four touched
exactly one source file, the one carrying the version number. 7.2.6 changed
both files, because it replaced `rlottie` with `tlottie` and preparation
started building a Rust library; the 7.2.5 to 7.2.7 range also rewrote 154 of
the 2883 sources. Read those paths in the upstream diff before promising
anyone a fast release.

Merging is the slow half now, and none of this speeds it up: the conflicts in
AyuGram-patched sources and the separate `lib_ui` and `lib_tl` merges are hand
work.

## Caches

Cold, a release costs an hour or two per platform to prepare the dependencies
and another two and a half to compile. Warm, the compile is minutes. Whether a
platform job takes ten minutes or five hours is decided entirely by whether
the six caches below were reachable and keyed correctly.

| Key prefix | Holds |
| --- | --- |
| `macos-universal-release-<toolchain>-<hash>` | `Libraries` and `ThirdParty` |
| `windows-x64-third-party-<hash>` | `ThirdParty` |
| `windows-x64-release-libraries-<hash>` | `Libraries\win64` |
| `ccache-macos-arm64-release-<commit>` | compiler cache |
| `ccache-macos-x86_64-release-<commit>` | compiler cache |
| `ccache-windows-x64-release-<commit>` | compiler cache |

The release job writes every one of them and, once a save succeeds, deletes
the older entries of the same prefix. A compiler cache key ends in the commit,
so without that deletion each release would leave its predecessor behind and
the repository would pass the ten gigabyte limit and start evicting the
entries it just wrote. A failed build still saves its compiler cache, so a
retry resumes from the objects the failed run did produce.

The Windows dependency keys hash the absolute build root along with
`prepare.py` and the SDK version. `prepare.py` writes a per-stage key for
every library that embeds that same absolute path, so a cache keyed without it
hits while every stage inside it misses: the job rebuilds Qt from source for
two hours and then skips the save because the outer cache hit. That is not
hypothetical. Moving the build from `C:\Users\runneradmin\TBuild` to the
workspace drive did exactly this and poisoned the cache for every release that
followed. Any future change to the build root must stay inside the key.

The build runs on the workspace drive, `D:`, because the runner image leaves
about 25 GB free on `C:` out of 150 GB, which a Release build does not fit
into. A build placed on `C:` gets through the compile and dies on the link,
three hours in. The Windows job prints `df -h` into the log for this reason —
the fuller report in the run summary cannot be read without a GitHub login.

`Cache keepalive` runs twice a week and restores every key prefix. GitHub
evicts a cache nothing has read for seven days; since 2025-11-20 that window
is configurable, but raising it requires a paid plan. Scheduled runs always
use the default branch, which is both the scope the release needs and the only
place GitHub will start them from. GitHub also disables scheduled workflows in
a repository with no activity for sixty days, which would stop the refreshing
silently.

The compiler cache key deliberately carries no toolchain fingerprint. `ccache`
already hashes the compiler through `compiler_check = content`, so a runner
image bump costs a few misses inside a restored directory instead of
discarding the directory. Dependency cache keys do carry a fingerprint,
because a library built by another toolchain is unusable rather than merely
stale. On macOS that fingerprint covers Xcode and the macOS SDK and nothing
else: a build driver like CMake cannot change what the libraries were linked
against, and including it would throw away a two-hour tree on every runner
image refresh.

Caching anything here at all requires `sloppiness = pch_defines,time_macros`,
because the large targets use precompiled headers. The price is `__DATE__`:
the build date in the About tooltip is the date the object was first compiled,
so a rebuilt release reports the date of the run its objects came from. On
Windows the cache also runs in depend mode, where a miss costs nothing beyond
the compile; without it every miss adds a full MSVC preprocessing pass over
the Qt headers, and a cold run, which is all misses, is exactly the one that
has to fit inside the job limit.

Both platforms prepare Qt with `qt-release-only`. The application is built
Release-only, so the Debug half of a static Qt is work nobody consumes.

Set the repository variable `TDESKTOP_API_ID` and secret `TDESKTOP_API_HASH`
to credentials obtained for the application through
[Telegram](https://core.telegram.org/api/obtaining_api_id). The workflow
validates them before any expensive job starts, because `configure` fails on
empty credentials only after the dependencies are built.

See [macOS](building-mac.md), [Windows](building-win.md) and
[Linux](building-linux.md) for the platform build commands. Windows and Linux
still require full build and runtime verification on this branch. A successful
macOS build does not establish compatibility on those platforms.

## Public release requirements

Technical maintenance releases use the following contract:

- Build the exact source commit for every advertised platform and architecture,
  and retain the workflow URL as release evidence.
- Use application API credentials registered for this distribution. Test-only
  credentials and another application's credentials are not a release setup.
- Do not bundle external translation snapshots. AyuGram translations are fetched
  by the application and cached locally.
- Verify the macOS ad-hoc signature and Windows Authenticode status, and state
  clearly that technical packages are not publisher-signed or notarized.
- Establish an authenticated update channel with its publisher, signing keys,
  version policy and supported platform IDs. Verify a real upgrade and rejection
  of altered or wrong-channel packages before enabling automatic installation.
- Publish checksums, exact source and pinned submodules with the binaries.
  Update the download instructions only when those binaries exist.

Technical release artifacts disable automatic updates explicitly. The source
updater is retained, but must not be pointed at an unrelated publisher or
enabled merely to expose an update button. There is no signed update channel in
this fork.

## Profiles

The normal macOS identity is `one.ayugram.AyuGramDesktop`, with the upstream
`AyuGram Desktop` Application Support directory. Development tests that need
isolation should use `-workdir` with a separate directory. Personal directory
names do not belong in the product defaults.

Close the application and back up its current profile before replacing a build.
Do not overwrite an existing profile automatically, silently merge accounts or
run two clients with copied authorization. Earlier experimental builds using a
different directory need an explicit local migration; this source change does
not perform one.

## Contributing upstream

The Telegram 7.2.8 update builds on
[AyuGramDesktop #460](https://github.com/AyuGram/AyuGramDesktop/pull/460).
Preserve its authorship and merge ancestry. The earlier macOS workflow proposal
[#427](https://github.com/AyuGram/AyuGramDesktop/pull/427) is related work.

`lib_ui` and `lib_tl` still point to the development repositories containing
the pinned commits. These are source dependencies, not application branding.
Upstream integration needs the corresponding submodule changes accepted before
the main repository pins them and restores the upstream URLs. Keep these URLs
absolute: a contributor must be able to fork only the main repository and still
clone its dependencies. Do not point at upstream before it contains the commits.

Keep language fixes independently reviewable from the Telegram version merge.
Start an integration PR as a draft until the advertised platform checks pass.
An open PR or a gap between releases is not evidence that upstream is abandoned.
