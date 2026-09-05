# Bundled AyuGram translations

These JSON files come from [AyuGram/Languages](https://github.com/AyuGram/Languages),
`values/langs/*/Shared.json` at commit
`087ab3232a9ac7d6d4ef506caa4bf60366042bbc`.
Translation credit belongs to that project's contributors.

All 24 non-English language packs in that revision are bundled. English uses
the application's compiled source strings. The bundles are an offline fallback;
the language loader still checks the upstream translation service for updates.
Translation completeness varies by language.

When refreshing this snapshot, validate every JSON object, update the matching
entries in `Resources/qrc/telegram/telegram.qrc`, and record the source commit
here. Do not machine-translate missing strings or change the selected language.
