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
check succeeds. A release that is already tagged still builds; only the
publishing step is skipped, so the pipeline can be exercised without
republishing and a release that failed after tagging can be retried.

A new build of a version that is already released takes the `revision` input:
`-f revision=2` publishes `v<version>-2` and names the source archive after it.
The application still reports the plain version, because its version names the
Telegram Desktop release it is built from, and the workflow accepts a revision
only for a version that already has its tag.

Both platform jobs report into the log and the run summary: time per CMake
target and the slowest translation units from `.ninja_log`, compiler cache
statistics, the processor count, and on macOS the swap used during
compilation. Read that report, not a stopwatch, when a build gets slower. A
compiler cache hit rate near zero explains an otherwise inexplicable
three-hour job, and swap above a few hundred megabytes means three parallel
compilers do not fit in the runner's memory.

## Releasing a new Telegram version

1. Branch from the default branch:
   `git switch -c codex/ayu-<version> origin/dev --no-track`. If AyuGram has
   released the same Telegram version, merge its `v<version>` tag and take
   their side in the application sources, except for this fork's changes they
   have not taken yet. Otherwise merge the Telegram Desktop tag and resolve the
   AyuGram-patched sources by hand. `lib_ui`, `lib_tl` and `codegen` carry
   AyuGram's patches; a Telegram Desktop tag that moves one of those pins
   before AyuGram does needs the submodule merged in a fork, and `.gitmodules`
   points at the fork until AyuGram has the commit.
2. Set the version in `Telegram/build/version` and add the release to
   `CHANGELOG.md`; the release notes link to its tagged copy. The workflow
   reads the version and requires the branch to be named `codex/ayu-<version>`.
   Upstream bumps the number in `Telegram/SourceFiles/core/version.h` and both
   files under `Telegram/Resources/winrc/` as well, and those lines carry
   AyuGram's product names, so all three conflict every time: keep the AyuGram
   side and raise its number by hand.
3. Optionally compile the branch for Linux first, in Telegram Desktop's
   published image, as [building-linux.md](building-linux.md) describes, with
   `-e CONFIG=Debug` and `-e KEEP_GOING=1` so that one pass lists every failing
   unit. With a warm compiler cache this takes minutes; the release workflow
   reaches the same error hours in. It does not compile the macOS- and
   Windows-only sources, and the release workflow compiles everything anyway.
4. Push the branch and let `Source checks` go green.
5. Dispatch the release **from the default branch**, naming the branch to
   build: `gh workflow run Release --ref dev -f ref=codex/ayu-<version>`,
   adding `-f revision=<n>` when the version is already released. The workflow
   file itself comes from the default branch, so a workflow change the release
   needs lands there first.

A rename in an upstream release conflicts nowhere: git keeps the AyuGram line
that uses the old name beside the upstream lines that no longer define it, and
only the compiler notices. Merging AyuGram's tag has a similar blind spot. Git
keeps every line this side changed and AyuGram did not, with no conflict to
point at it. Diff the result against their tag,
`git diff <their tag> HEAD -- Telegram`, and make every remaining difference
one the fork means to keep.

Dispatching from the default branch is not a convenience. A run reaches only
the caches of its own ref and of the default branch, and the release branch is
renamed every version, so a release dispatched on its own branch would write
caches nothing else can ever read and start cold every time. The workflow
refuses to run anywhere but the default branch for that reason, and which
branch is the default must not change. Moving the `dev` tip is fine, because
caches are scoped to the ref name.

A failed or cancelled build still saves its compiler cache, so cancel a run as
soon as it is known to fail: the retry resumes from the objects it produced.

An upstream release that changes `Telegram/build/prepare/**` or
`Telegram/build/qt_version.py` invalidates the dependency caches, and
rebuilding them costs an hour or two per platform. New `lib_ui` headers
invalidate a large share of the compiler cache. Read those paths in the
upstream diff before promising anyone a fast release. When preparation
changes, compare the `Libraries` strip in `release.yml` with the one in
upstream's `canary.yml`: the job caches the tree only after that strip, and a
file the strip wrongly removes fails the next build that restores the cache.

Merging is the slow half, and none of this speeds it up. It is short when
AyuGram has released the version first. When the fork goes ahead of them, the
AyuGram-patched sources and any submodule merges are hand work.

## Caches

Whether a release takes twenty-five minutes or four hours is decided by whether
the six caches below were reachable and keyed correctly. Measured on 7.2.8, the
Windows job costs 4h03m with every cache cold and 24m with every cache warm;
inside it, preparing the dependencies falls from 1h46m to under ten seconds and
compiling from 2h01m to 11m25s. The macOS path costs about ten minutes warm,
both architectures and the universal package included.

| Key prefix | Holds |
| --- | --- |
| `macos-universal-release-<toolchain>-<hash>` | `Libraries` and `ThirdParty` |
| `windows-x64-third-party-<hash>` | `ThirdParty` |
| `windows-x64-release-libraries-<hash>` | `Libraries\win64` |
| `ccache-macos-arm64-release-<commit>` | compiler cache |
| `ccache-macos-x86_64-release-<commit>` | compiler cache |
| `ccache-windows-x64-release-<commit>` | compiler cache |

The release job writes every one of them and deletes the entries its own save
supersedes, because a compiler cache key ends in the commit and every release
would otherwise leave its predecessor behind. The dependency caches are pruned
after their save and the compiler caches before theirs, and the order is the
whole point: three compiler caches coexisting with their predecessors come to
about eleven gigabytes, which passes the limit and evicts by least recent use,
and the entry least recently used is a dependency tree that costs two hours to
rebuild. Deleting first is safe only for a compiler cache, which one run
refills. A successful build also evicts every object it did not use before the
save. Without that, each version leaves the previous one's objects behind, the
compiler caches fill to their maximum, and the six entries pass the limit.

The Windows compiler cache is three gigabytes rather than two. A Release build
compiles about 2550 translation units, which occupy 2.2 GB; in two gigabytes
the cache evicted its own entries while the build was still running, and the
compile took 28m09s at 74% hits against 11m26s at 99%. macOS uses under one
gigabyte for the same source, because its objects carry no MSVC debug records.

The Windows dependency keys hash the absolute build root along with
`prepare.py` and the SDK version. `prepare.py` writes a per-stage key for
every library that embeds that same absolute path, so a cache keyed without it
hits while every stage inside it misses: the job rebuilds Qt from source for
two hours and then skips the save because the outer cache hit. Any change to
the build root must stay inside the key.

The build runs on the workspace drive, `D:`, because the runner image leaves
about 25 GB free on `C:`, which a Release build does not fit into: a build
placed on `C:` gets through the compile and dies on the link, three hours in.
The Windows job prints `df -h` into the log for this reason, since the fuller
report in the run summary cannot be read without a GitHub login.

`Cache keepalive` runs daily and looks every key prefix up without downloading
it: a lookup counts as a read. GitHub evicts a cache nothing has read for seven
days; raising that window requires a paid plan. Each path is written exactly
as the release job's runner sees it, because the path is hashed into the cache
entry's version, and a lookup that misses fails the job. On Windows the
version also carries a Windows-only marker, so the Windows entries need a
Windows runner. Elsewhere it does not depend on the runner, and the macOS
entries are looked up from Linux with the macOS workspace path written out:
macOS runners are the ones in short supply, and a keepalive that waits for one
refreshes nothing. Scheduled runs always use the default branch, which is both
the scope the release needs and the only place GitHub will start them from.
GitHub also disables scheduled workflows in a repository with no activity for
sixty days, which would stop the refreshing silently.

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

The dependency build runs with the compiler cache switched off. Its output is
cached as a whole tree, so the objects would only crowd the application's out
of the cache budget, and on Windows the cache is actively harmful: `meson`
takes `ccache` from `PATH` as the compiler launcher and then parses the
`/showIncludes` output it wraps, so a cache configured to rewrite paths makes
`meson setup` fail outright on every library it builds.

Both platforms prepare Qt with `qt-release-only`. The application is built
Release-only, so the Debug half of a static Qt is work nobody consumes.

Set the repository variable `TDESKTOP_API_ID` and secret `TDESKTOP_API_HASH`
to credentials obtained for the application through
[Telegram](https://core.telegram.org/api/obtaining_api_id). The workflow
validates them before any expensive job starts, because `configure` fails on
empty credentials only after the dependencies are built.

See [macOS](building-mac.md), [Windows](building-win.md) and
[Linux](building-linux.md) for the platform build commands. The workflow
builds the Windows packages but does not run them, and Linux is compiled only
by the check above, never packaged.

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
run two clients with copied authorization.

## Contributing upstream

The fork builds on AyuGram's releases and merges a Telegram Desktop release
itself only while AyuGram has not released it. A change worth having upstream
goes to AyuGram as a pull request of its own against `dev`, separate from any
version merge, so that it can be reviewed and taken alone. Start it as a draft
until the advertised platform checks pass. An open PR or a gap between releases
is not evidence that upstream is abandoned.

A fix to Telegram Desktop's own code, which AyuGram carries unchanged, goes to
both projects: one pull request to `telegramdesktop/tdesktop` from a branch off
its `dev`, and the same change to AyuGram from a branch off AyuGram's `dev`,
each description linking the other. AyuGram takes Telegram Desktop releases
with a delay, so its own pull request is what gets the fix to AyuGram until
then. Read the port instead of trusting a clean cherry-pick: AyuGram's base is
older, and the same line can need different code there.

`.gitmodules` points at AyuGram's `lib_ui`, `lib_tl` and `codegen`, or at this
fork's copy of one while its pin needs a merge AyuGram has not published. Keep
the URLs absolute: a contributor must be able to fork only the main repository
and still clone its dependencies. Pin only a commit that sits on a branch of
the repository the URL names, and keep that branch. AyuGram rebases its patches
in these repositories onto each new upstream and force-pushes them, so a pin
taken from an older branch can end up on no branch at all.
