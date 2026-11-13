# Changelog

## [0.2.0] — 2026-11-13

### Breaking

- **Tool names now use underscores instead of dots.** The separator in every
  name changed from `.` to `_`: `pim` + `.` + `validate` → `pim_validate`,
  and likewise for `gtin_check`, `gtin_structure`, and `sscc_check`
  (`pim_gtin_check`, `pim_gtin_structure`, `pim_sscc_check`). The provider
  validates every `tools[].name` against `^[a-zA-Z0-9_-]+$`; a dotted name makes
  it reject the whole `tools` array (`Invalid 'tools[N].name'`), so the plugin
  registered but no request carrying the tools could succeed. Dotted aliases
  cannot be put on the wire, so no compatibility alias is kept: callers must
  migrate to the underscore names. This is the minor bump that the 0.1.x
  compatibility promise requires for a breaking change.
- Added `test/tool-name-wire.test.mjs`: every registered tool name must match
  `^[a-zA-Z0-9_-]+$`, contain no dot, stay in the `pim_` namespace and be unique.
- README (five languages), `TROUBLESHOOTING.md`, the flow diagrams, the
  quickstart runner, the acceptance script and the tool names in source and
  tests were updated with the rename.

## [0.1.0] — 2026-11-03

### Stable

- First non-alpha release: tool names and the CLI surface are covered by a
  compatibility promise (breaking changes require a minor bump).
- Ships a quickstart sample, a one-line prompt, a permission block and real captures.

## [0.1.0] — 2026-11-01

### Security / Fixes

- Release configuration hardening: wider host peer range and a build step before publish.


### Added

- SSCC check tool: SSCC validation (18 digits, GS1 mod-10 check digit) with distinct format and checksum codes. Verified by `node --test test/*.test.mjs` (8/8).

## [Unreleased]

### Added

- GTIN structure tool: GTIN-8/12/13/14 decomposition with the GTIN-14 packaging indicator and variable-measure flag (GS1 General Specifications).
- Whole-table validation now reports duplicate GTINs (`E_PIM_GTIN_DUPLICATE`) and over-precise prices (`E_PIM_PRICE_PRECISION`).
- Verified by `node --test test/pim.test.mjs` (5/5); fixtures are our own public/synthetic rows.

## [0.1.0-alpha.7] — 2026-11-01

### Changed

- Documentation: five-language fixture/acceptance links now resolve on npm; added specific related-checker/tool links.
- Marketplace metadata: taxonomy category, archetype, domains and status; docs page now shows the same.

All notable changes to `dsh-pim-lint` are documented here. The format follows Keep a Changelog; this project uses alpha versions.

## [0.1.0-alpha.6] — 2026-11-01

### Added

- Five-language READMEs: English, 简体中文, Español, Português, हिन्दी.
- Local workflow SVG at `docs/assets/dsh-pim-lint-flow.svg`.
- Family cross-links (domain index, checker family, `dsh-kit`), compatibility, permissions, and related-work sections.
- Standard repository files: `SECURITY.md`, `PRIVACY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, and `icon.svg`.

### Changed

- README aligned with the PerryLink DSH checker/plugin family style; package remains public/synthetic, alpha, not GA.

### Maintenance

- 2026-11-01: active again — feature work, hardening and fresh evidence resumed.

## [Earlier]

Earlier alpha builds are available from npm and GitHub Releases; this file starts at the family-standard documentation wave.
