# Changelog

## 7.4.3 - 2026-11-13

- Updated the application base to Telegram Desktop 7.4.3 ahead of an AyuGram
  release of it: replies to forwarded messages with an instant local bubble,
  a voice and round messages filter in shared media, multiple selection in
  the contacts and proxy lists, Ctrl+O to replace media while editing a
  caption, and fixes for a freeze when a screen reader reads a long history,
  a crash opening media of unsent scheduled messages, file selection in mini
  apps and a squeezed maximized window on Windows.
- The contacts list keeps AyuGram's mutual contact mark and its hint on
  click: Telegram Desktop 7.4.3 moved the list into its own box with
  selectable rows, and the mark moved with it.
- `lib_ui` comes from this fork's copy of AyuGram's branch with Telegram
  Desktop 7.4.3 merged in; `codegen` and `lib_tl` did not move.

## 7.4.2 - 2026-11-11

- Updated the application base to Telegram Desktop 7.4.2 ahead of an AyuGram
  release of it: Qt's HTTP response limits for CVE-2026-116337, a chats column
  and a third column of its own for each window, restored on relaunch, inline
  video playback up to 1920x1920, and fixes for the first message missing
  from a just-created topic, two chat lists shown at once when switching
  filters and a crash on quit with the story views menu open.
- The userpic in the notification preview keeps AyuGram's corner radius and
  takes Telegram Desktop's smoothing, which fixes its blurry edge.
- `lib_ui`, `codegen` and `lib_tl` did not move.

## 7.4.1 - 2026-11-09

- Updated the application base to Telegram Desktop 7.4.1 ahead of an AyuGram
  release of it, with 7.4.0: interactive widgets in bot messages, payments
  and data signing for them through Gram Wallet's TON Connect window, a fix
  for a crash at launch and several other crash fixes.
- An incoming message is now counted as unread before the new chat view can
  see it. Since 7.3.3 the count was raised before the chat was notified of the
  message, but the new chat view, the default since 7.3.5, can read it
  earlier still, while the message is being indexed. In a chat with no
  messages shown, that read never reached the server and other devices kept
  the message unread.
- `lib_ui` comes from this fork's copy of AyuGram's branch with Telegram
  Desktop 7.4.1 merged in; `codegen` and `lib_tl` did not move.

## 7.3.5 - 2026-11-04

- Updated the application base to Telegram Desktop 7.3.5 ahead of an AyuGram
  release of it, with the changes of the 7.3.4 beta: the new chat view for
  everyone, search tabs for apps, channels and media, and a large set of
  security and crash fixes.
- Kept AyuGram's music row with the cover in profiles. Telegram Desktop 7.3.5
  moved profile music into a pill under the action buttons; that pill stays
  hidden so the track is not shown twice, while the balance pill works as in
  Telegram Desktop.
- Clear the ID search selection together with the other search rows, which
  the new deselect-on-top step of the chat search can now reach.
- `lib_ui` comes from this fork's copy of AyuGram's branch with Telegram
  Desktop 7.3.5 merged in; `codegen` and `lib_tl` did not move.

## 7.3.3 - 2026-10-22

- Updated the application base to Telegram Desktop 7.3.3 ahead of an AyuGram
  release of it, with the fixes of 7.3.2 and 7.3.3. The base also carries
  AyuGram's unreleased fix that honors the similar channels setting in search.
- Fixed incoming messages that stayed unread on other devices after being
  read here. A chat open at the bottom could read a new message before its
  unread count included it, and the read never reached the server, so other
  devices kept the unread badge and the notification.
- The Windows build moves from Qt 5 to Qt 6, as Telegram Desktop 7.3.2 did.
- `lib_ui` comes from this fork's copy of AyuGram's branch with Telegram
  Desktop 7.3.3 merged in; `codegen` keeps its 7.3.1 copy, which 7.3.3 did
  not move.

## 7.3.1 - 2026-10-12

- Updated the application base to Telegram Desktop 7.3.1 ahead of an AyuGram
  release of it. This brings the wallet added in 7.3, Unicode 17 emoji from
  7.2.10, and the fixes of both.
- `lib_ui` and `codegen` come from this fork's copies of AyuGram's branches
  with Telegram Desktop 7.3.1 merged in, until AyuGram publishes the same pins.
- Keep the generated wallet engine sources in the cached dependency tree, as
  Telegram Desktop's own workflow does.

## 7.2.9-3 - 2026-10-05

- Strip local symbols from the macOS executable. The release step removed only
  debugging entries and left about two million local symbols, so the
  executable weighed 1.75 GB; it is now about 0.6 GB, and the disk image
  shrinks with it.

## 7.2.9-2 - 2026-10-05

- Based the fork on AyuGram 7.2.9 instead of its own merge of Telegram
  Desktop 7.2.9. This brings AyuGram's rework of view-once media, its crash
  fixes and stricter link handling, and window screenshot protection disabled
  on macOS and Windows. `lib_ui`, `lib_tl` and `codegen` come from AyuGram's
  repositories again.
- Kept the language synchronization and macOS icon fixes, which AyuGram does
  not have yet, and two parts of Telegram Desktop 7.2.9 that AyuGram's merge
  dropped: the guard against rebuilding a chat badge on selection, and the
  reply handling of a send that ghost mode schedules.
- Publish a new build of an already released version under a revision tag,
  such as this `v7.2.9-2`, while the application keeps the Telegram version.

## 7.2.9 - 2026-09-17

- Updated the application base to Telegram Desktop 7.2.9.
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
