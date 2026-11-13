# 故障排查 — dsh-pim-lint

每条按「症状 / 原因 / 动作」写。报错原文都是 `<一句人话>（E_XXX）｜下一步：<动作>`，
把 `E_XXX` 和这句话一起发到 issue 即可定位；不要把真实商品表贴进 issue。

## 1. CSV 只有表头，没有商品行（E_PIM_CSV_EMPTY）

- **症状**：`这个 CSV 里只有表头，没有商品行（E_PIM_CSV_EMPTY）｜下一步：在表头下面补至少一行商品再跑一次`
- **原因**：导出时只勾了表头，或数据行被 Excel 的筛选隐藏后另存。
- **动作**：确认表头下面至少有一行商品，用「另存为 → CSV UTF-8」重新导出。

## 2. 表头缺列（E_PIM_HEADER）

- **症状**：`CSV 表头缺少必填列（E_PIM_HEADER）｜下一步：把表头改成 sku,title,gtin,price 四列（大小写不限）`
- **原因**：表头写成了中文（商品编码 / 名称 / 条码 / 单价），或四列名字拼错。
- **动作**：把第一行改成 `sku,title,gtin,price`；其他列可以保留，列序不限。

## 3. 某行列数和表头对不上（E_PIM_CSV_ROW）

- **症状**：`有一行的列数和表头对不上（E_PIM_CSV_ROW）｜下一步：用 Excel 另存为 CSV 重新导出，确保每行都是四列、没有多余逗号`
- **原因**：商品标题里带半角逗号却没有加引号，或某行多 / 少一个逗号。
- **动作**：含逗号的标题用英文双引号包起来（`"保温杯, 500ml"`），再导出一次。

## 4. 条码校验不通过（E_PIM_GTIN_INVALID / E_PIM_SSCC_CHECKSUM）

- **症状**：问题清单里出现 `E_PIM_GTIN_INVALID`，或 SSCC 结果里出现 `E_PIM_SSCC_CHECKSUM`。
- **原因**：条码抄错一位、用了内部码，或 SSCC 由系统生成时少一位。
- **动作**：用 `pim_gtin_structure` 复核位数和指示位（GTIN-14 首位 9 表示变量度量商品）；SSCC 固定 18 位、末位是 mod-10 校验位。

## 还不行

```sh
node samples/quickstart/run.mjs --check   # 自带样例必须通过
node --test test/*.test.mjs               # 10 项测试
```

仍失败时请在 <https://github.com/PerryLink/dsh-pim-lint/issues> 附上：包版本、最小合成输入、完整报错那一行。
