# dsh-pim-lint

> 🧊 **FROZEN — 2026-10-31. No new features.** This public/synthetic S1 demo is not GA; it stays installable and only genuine breakage is fixed.

## Maintenance status: 🧊 FROZEN

Frozen on 2026-10-31. This repository is a public/synthetic S1 demo, not a validated product. The npm package stays installable; no new features are planned.


PIM catalog lint for required fields, duplicate SKU, GTIN check digit and price for DeepSeek Harness.

> **Status: alpha / public-synthetic / partial / not counted / not GA.** No customer evidence, customer data, or production-readiness claim. All acceptance rows are `counted=false`.

## Install

```sh
dsh plugin --profile <profile> add dsh-pim-lint
dsh --profile <profile> --dump-config | grep dsh-pim-lint
```

Requires DSH `>=0.2.1-rc.3 <0.3.0` and Node `>=24.9 <25`.

<details>
<summary>中文摘要</summary>

PIM 目录 lint：必填、重复 SKU、GTIN 校验位与价格。 安装：`dsh plugin --profile <profile> add dsh-pim-lint`。公开/合成、alpha、非 GA。

</details>

## Tools

| Tool | What it does | Risk |
|---|---|---|
| `pim.validate` | Validate `sku,title,gtin,price` CSV rows and return issues | R0 |
| `pim.gtin_check` | Check GTIN-8/12/13/14 check digits | R0 |

## Input / output

**Input:** a `sku,title,gtin,price` CSV. **Output:** an issue list (missing fields, duplicate SKU, invalid GTIN, invalid price). This is a lint, not a PIM.

## Limits / non-claims

- Not a PIM, channel listing tool, Amazon/Shopify integration, or a replacement for SKU-14.
- No image, taxonomy, localization, or marketplace schema handling.
- Synthetic catalog fixtures only; no real seller catalog.
- No customer evidence, customer data, or production-readiness claim; all fixtures are public/synthetic.

## Public sample

Synthetic catalog rows; `ACCEPTANCE.csv` lists 3 public checks.

## Development

```sh
pnpm install --frozen-lockfile
pnpm build && pnpm lint && pnpm typecheck && pnpm test && pnpm gate
```

## License

Apache-2.0. See `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES`.
