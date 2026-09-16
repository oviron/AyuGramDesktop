# Changelog

## Unreleased

- Build and publish a release from a single workflow, dispatched on the default
  branch so it writes the caches every release branch can read. A version is
  now compiled once instead of once to warm the caches and again to publish.
- Key the Windows dependency caches by the build root. `prepare.py` embeds it
  in every per-stage key, so a cache keyed without it hit while every stage
  inside it missed, rebuilding Qt from source on each release.
- Prepare Qt Release-only on both platforms; the application is built
  Release-only and nothing consumed the Debug half.
- Cache the Windows compiler for the first time, refresh every cache twice a
  week against the seven-day eviction, and drop each superseded entry after a
  successful save.
- Report per-target build times, compiler cache statistics and the processor
  count in the build log as well as the run summary, and attribute Windows
  objects to their real targets instead of to the drive letter.

## 7.2.8 - 2026-09-15

- Updated the application base to Telegram Desktop 7.2.8, which fixes crashes
  on invalid Lottie files.
- Picked up the 7.2.6 feature release: image editor text tool, folder and file
  set sending, GIF editing before send, and call rating in the call panel.
- Replaced the rlottie animation library with tlottie, following upstream;
  preparation now builds a Rust static library under ThirdParty.
- Built the two macOS architectures in separate release jobs, because one cold
  universal build exceeds the six-hour job limit.

## 7.2.5 - 2026-09-06

- Updated the application base to Telegram Desktop 7.2.5.
- Preserved AyuGram features and upstream attribution without fork-specific branding.
- Fixed language synchronization, macOS bundle identity and application icons.
- Added reproducible technical packages for universal macOS and Windows x64.
- Disabled automatic updates until a signed update channel is available.
