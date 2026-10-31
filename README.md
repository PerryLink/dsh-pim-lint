# @perrylink/dsh-pim-lint

**PUBLIC/SYNTHETIC DEMO — PARTIAL — NOT COUNTED — NOT GA.**

A small PIM catalog lint for DeepSeek Harness: validate `sku,title,gtin,price` CSV rows, duplicate SKU, GTIN check digit, and price. This is **not** a PIM, channel listing tool, Amazon/Shopify integration, or a replacement for SKU-14.

## Tools

| Tool | What it does | Risk |
|---|---|---|
| `pim.validate` | Validate a CSV catalog and return issues | R0 |
| `pim.gtin_check` | GTIN-8/12/13/14 check digit | R0 |

## Install

```sh
dsh plugin --profile <profile> add @perrylink/dsh-pim-lint
```

No customer data, channel schema, or real seller catalog is included.
