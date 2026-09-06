# Build instructions for macOS

Use a recursive checkout of the repository and branch you intend to build.
Its parent directory holds `Libraries` and `ThirdParty`; keep application
profiles outside those build directories. Allow at least 55 GB for a cold
universal build.

Install Xcode and Homebrew first. CI uses Xcode 16.4 on `macos-15`; the `.icns`
fallback does not require Xcode 26's Icon Composer.

```bash
brew install git automake libtool cmake pkg-config ninja nasm meson ccache
```

Select the installed Xcode using `xcode-select` if necessary. Obtain your own
`TDESKTOP_API_ID` and `TDESKTOP_API_HASH` as described in
[Telegram's application registration instructions](https://core.telegram.org/api/obtaining_api_id)
and export them in the build shell. Do not commit credentials.

## Release preview

The release workflow builds `arm64` and `x86_64` separately, then combines every
architecture-dependent Mach-O file with `lipo`. This preserves Swift-based local
translation, which CMake cannot configure with multiple values in
`CMAKE_OSX_ARCHITECTURES`.

For a local single-architecture Release build:

```bash
./Telegram/build/prepare/mac.sh silent qt-release-only
cd Telegram
./configure.sh -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  "-DCMAKE_Swift_FLAGS=-target arm64-apple-macos11.0" \
  -DDESKTOP_APP_MAC_ARCH=arm64 \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache \
  -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
  "-DTDESKTOP_API_ID=$TDESKTOP_API_ID" \
  "-DTDESKTOP_API_HASH=$TDESKTOP_API_HASH" \
  -DDESKTOP_APP_DISABLE_AUTOUPDATE=ON
python3 build/check_macos_release.py ../out \
  --architectures arm64
cmake --build ../out --parallel 3 --target Telegram
```

The result is `out/AyuGram.app`. Preview builds are not a public signed release;
see [release requirements](releasing.md).

Append `mac-arm64` to preparation when only Apple Silicon dependencies are
needed. For Intel only, use `mac-x86_64` and `x86_64` instead. Do not configure
a single CMake tree with both architectures while Swift translation is enabled;
use `x86_64-apple-macos10.13` for the Intel Swift target.
Other dependencies retain their upstream universal build recipes.

## Debug and Xcode development

Without `qt-release-only`, preparation retains the upstream defaults: universal
Qt with Debug and Release configurations. `skip-release` builds Debug Qt only;
it cannot be combined with `qt-release-only`. Do not reuse a Release-only Qt
installation for a Debug application without rerunning preparation.

Omit `-G Ninja` to use Xcode. Open `out/Telegram.xcodeproj` and choose the
configuration there. Use Release for daily use and distribution.

## CI and updates

The `Release` workflow checks generated compiler commands and Qt linkage for
both architecture builds, then checks the combined bundle identity, icon and
packaged architectures before creating the DMG. Credentials come from repository
configuration, not from a branch. The full build is not triggered on push.

Automatic updates remain disabled for these preview packages until the
distribution has a verified signing and update channel. This does not change
the source default for maintainers building official releases.
