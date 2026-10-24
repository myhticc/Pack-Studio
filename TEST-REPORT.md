# Pack Studio 1.0.0 — verification report

Artifact: `dist/PackStudio.exe`

- Windows x64 PE executable, 315,460,746 bytes (300.8 MiB).
- SHA-256: `1dac8788dc5a04064da962517b13d99e92b303cea09ebbc15cfc1ff61d0df69a`
- Single delivered file. Bundled Fixed WebView2 Runtime 156.0.4314.42; no dependency on a system WebView2 installation is used by the launcher.
- First-run extraction and subsequent app startup passed from the packaged EXE, without the development `--dev` path.
- Native C++ tests: 37/37 passed, including all 24 target formats, PNG color/alpha, project archives, untouched imported file bytes, draft exclusion, missing resources, invalid JSON, ZIP limits and Unicode atomic file operations.
- Actual embedded WebView2 editor tests: 9/9 passed, including drawing undo/redo, flood fill boundaries, library layers, project serialization, color replacement, both armor UV textures, six block faces, C++ validation and actual WebGL draw calls.
- Native Mojang download test passed: official client retrieval, manifest size/SHA-1 verification, extraction and texture lookup.
- 570 bundled library assets, including 12 body/leggings armor template pairs and original CC0 source attribution.

## Real Minecraft

- Minecraft 1.20: PASS — exported pack loaded in a real, hidden game renderer; diamond sword resource bytes matched the export.
- Minecraft 1.21.2: PASS — exported pack loaded in a real, hidden game renderer; diamond sword resource bytes matched the export.
- Minecraft 1.21.9: PASS — exported pack loaded in a real, hidden game renderer; diamond sword resource bytes matched the export.
- Minecraft 1.21.11: PASS — exported pack loaded in a real, hidden game renderer; diamond sword resource bytes matched the export.
- Minecraft 26.3: PASS — exported pack loaded in a real, hidden game renderer; diamond sword resource bytes matched the export.

Tests used isolated offline game profiles and hidden native windows. No desktop input, browser control or live player account was used. These tests verify pack activation and resource selection; they do not claim that every edited texture was inspected during gameplay.

## Limits of verification

A separate clean Windows 10/11 virtual machine was not available. The packaged app was tested on the current Windows machine with its own explicitly selected fixed runtime; the installed WebView2 runtime was not used. Windows 10 execution and GPU differences on other machines therefore remain unverified. The build is unsigned.

Arbitrary third-party custom models are preserved, not automatically migrated or fully previewed. Future Minecraft releases require a verified version adapter update. Six-face model generation intentionally targets simple full cubes; existing complex block models are preserved.
