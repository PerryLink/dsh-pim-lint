import { defineTool } from '@deepseek-ai/dsh-tools'
import { gtinInfo, gtinValid, parseCsv, ssccCheck, validateRows } from '../core/pim.js'
const text = (t: string) => [{ type: 'text' as const, text: t }]
export function createTools() {
  const validate = defineTool({
    name: 'pim_validate',
    description: 'Validate a public/synthetic PIM CSV (sku,title,gtin,price): required fields, duplicate SKU, GTIN check digit, non-negative price. Read-only; no channel submission.',
    parameters: { csv_text: { type: 'string', required: true } },
    output: { schema: { type: 'object', additionalProperties: false, properties: { rows: { type: 'number', required: true }, issues: { type: 'array', required: true, items: { type: 'object', additionalProperties: false, properties: { sku: { type: 'string', required: true }, field: { type: 'string', required: true }, code: { type: 'string', required: true } } } } } }, render: (_a, v) => text(`pim rows=${v.rows} issues=${v.issues.length}`) },
    async execute(args) {
      const rows = parseCsv(args.csv_text)
      return { rows: rows.length, issues: validateRows(rows) }
    },
  })
  const gtin = defineTool({
    name: 'pim_gtin_check',
    description: 'Check a GTIN-8/12/13/14 check digit. Read-only.',
    parameters: { gtin: { type: 'string', required: true } },
    output: { schema: { type: 'object', additionalProperties: false, properties: { gtin: { type: 'string', required: true }, valid: { type: 'boolean', required: true } } }, render: (_a, v) => text(`${v.gtin} ${v.valid ? 'ok' : 'invalid'}`) },
    async execute(args) { return { gtin: args.gtin, valid: gtinValid(args.gtin) } },
  })
  const gtinStructure = defineTool({
    name: 'pim_gtin_structure',
    description: 'Decompose a GTIN (8/12/13/14 digits): format, check digit validity, packaging indicator and variable-measure flag per GS1 General Specifications. Read-only.',
    parameters: { gtin: { type: 'string', required: true } },
    output: { schema: { type: 'object', additionalProperties: false, properties: { gtin: { type: 'string', required: true }, valid: { type: 'boolean', required: true }, format: { type: 'string', required: true }, indicator: { type: 'number' }, variable_measure: { type: 'boolean', required: true } } }, render: (_a, v) => text(`${v.gtin} ${v.format} ${v.valid ? 'ok' : 'invalid'}`) },
    async execute(args) { const info = gtinInfo(args.gtin); return { ...info, indicator: info.indicator ?? undefined } },
  })
  const sscc = defineTool({
    name: 'pim_sscc_check',
    description: 'Check an SSCC (18 digits, GS1 mod-10 check digit). Read-only.',
    parameters: { sscc: { type: 'string', required: true } },
    output: { schema: { type: 'object', additionalProperties: false, properties: { sscc: { type: 'string', required: true }, valid: { type: 'boolean', required: true }, reason: { type: 'string' } } }, render: (_a, v) => text(`${v.sscc} ${v.valid ? 'ok' : 'invalid'}`) },
    async execute(args) { return ssccCheck(args.sscc) },
  })

  return [validate, gtin, gtinStructure, sscc]
}
