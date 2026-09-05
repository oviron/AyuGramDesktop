# Building and releasing AyuGram

The application keeps AyuGram's name, icons, feature defaults and platform
identifiers. Repository ownership is not application branding. A development
fork must identify where its binaries come from; it must not claim to be an
official upstream release.

## Build checks

`Source checks` runs on pushes and pull requests without production credentials.
It checks build options, translation resources and workflow syntax. It does not
compile the C++ application.

`AyuGram macOS` runs manually from Actions on the selected branch. It supports
`universal` (the default), `arm64` and `x86_64`. Versioned filenames come from
`Telegram/build/version`, not the workflow. Set the repository variable
`TDESKTOP_API_ID` and secret `TDESKTOP_API_HASH` to credentials obtained for the
application through [Telegram](https://core.telegram.org/api/obtaining_api_id).
Missing credentials stop the job before dependency preparation.

The workflow produces Release preview artifacts with source commit, architecture
and SHA-256 records. Dependencies and compiler results have separate caches;
architecture and toolchain changes do not share a final cache key. Full builds
are manual because a cold macOS build takes hours on hosted runners.

See [macOS](building-mac.md), [Windows](building-win.md) and
[Linux](building-linux.md) for the platform build commands. Windows and Linux
still require full build and runtime verification on this branch. A successful
macOS build does not establish compatibility on those platforms.

## Public release requirements

Before publishing a release:

- Build the exact source commit for every advertised platform and architecture.
  Test startup, login, selected language, updates and the AyuGram features on
  each supported platform. Keep build/run links with the release evidence.
- Use application API credentials registered for this distribution. Test-only
  credentials and another application's credentials are not a release setup.
- Confirm redistribution terms for all bundled assets, including the translation
  snapshot from `AyuGram/Languages`, and retain author attribution.
- Sign public macOS packages with the publisher's Developer ID, notarize them
  and verify Gatekeeper acceptance. The current workflow's ad-hoc signature only
  checks package integrity; it is not publisher authentication or notarization.
- Establish an authenticated update channel with its publisher, signing keys,
  version policy and supported platform IDs. Verify a real upgrade and rejection
  of altered or wrong-channel packages before enabling automatic installation.
- Publish checksums, exact source and pinned submodules with the binaries.
  Update the download instructions only when those binaries exist.

Preview artifacts disable automatic updates explicitly. The source updater is
retained, but must not be pointed at an unrelated publisher or enabled merely
to expose an update button. There is no new signing service or public release
channel configured by this branch.

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
