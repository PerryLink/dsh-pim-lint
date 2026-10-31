import { defineTool } from '@deepseek-ai/dsh-tools'
import { gtinValid, parseCsv, validateRows } from '../core/pim.js'
const text = (t: string) => [{ type: 'text' as const, text: t }]
export function createTools() {
  const validate = defineTool({
    name: 'pim.validate',
    description: 'Validate a public/synthetic PIM CSV (sku,title,gtin,price): required fields, duplicate SKU, GTIN check digit, non-negative price. Read-only; no channel submission.',
    parameters: { csv_text: { type: 'string', required: true } },
    output: { schema: { type: 'object', additionalProperties: false, properties: { rows: { type: 'number', required: true }, issues: { type: 'array', required: true, items: { type: 'object', additionalProperties: false, properties: { sku: { type: 'string', required: true }, field: { type: 'string', required: true }, code: { type: 'string', required: true } } } } } }, render: (_a, v) => text(`pim rows=${v.rows} issues=${v.issues.length}`) },
    async execute(args) {
      const rows = parseCsv(args.csv_text)
      return { rows: rows.length, issues: validateRows(rows) }
    },
  })
  const gtin = defineTool({
    name: 'pim.gtin_check',
    description: 'Check a GTIN-8/12/13/14 check digit. Read-only.',
    parameters: { gtin: { type: 'string', required: true } },
    output: { schema: { type: 'object', additionalProperties: false, properties: { gtin: { type: 'string', required: true }, valid: { type: 'boolean', required: true } } }, render: (_a, v) => text(`${v.gtin} ${v.valid ? 'ok' : 'invalid'}`) },
    async execute(args) { return { gtin: args.gtin, valid: gtinValid(args.gtin) } },
  })
  return [validate, gtin]
}
