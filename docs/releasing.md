# Building and releasing AyuGram

The application keeps AyuGram's name, icons, feature defaults and platform
identifiers. Repository ownership is not application branding. A development
fork must identify where its binaries come from; it must not claim to be an
official upstream release.

## Build checks

`Source checks` runs on pushes and pull requests without production credentials.
It checks build options and workflow syntax, but does not compile the C++
application.

`Release` runs only by an explicit manual dispatch. It validates the version
before starting the expensive jobs, then builds universal macOS and Windows x64
packages plus the full recursive source archive. Dependencies and compiler
results use separate caches. The workflow creates the tag and public GitHub
Release only after every build and package check succeeds.

Set the repository variable `TDESKTOP_API_ID` and secret `TDESKTOP_API_HASH` to
credentials obtained for the application through
[Telegram](https://core.telegram.org/api/obtaining_api_id). Missing credentials
stop platform jobs before dependency preparation.

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

The Telegram 7.2.5 update builds on
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
