export interface PimRow { sku: string; title: string; gtin: string; price: string }
export interface PimIssue { sku: string; field: string; code: string }

export type PimErrorCode = 'E_PIM_CSV_EMPTY' | 'E_PIM_HEADER' | 'E_PIM_CSV_ROW'

/** User-facing wording: one plain sentence, the code, then exactly one next action. */
const PIM_HUMAN: Record<PimErrorCode, { text: string; next: string }> = {
  E_PIM_CSV_EMPTY: { text: '这个 CSV 里只有表头，没有商品行', next: '在表头下面补至少一行商品再跑一次' },
  E_PIM_HEADER: { text: 'CSV 表头缺少必填列', next: '把表头改成 sku,title,gtin,price 四列（大小写不限）' },
  E_PIM_CSV_ROW: { text: '有一行的列数和表头对不上', next: '用 Excel 另存为 CSV 重新导出，确保每行都是四列、没有多余逗号' },
}

export class PimError extends Error {
  readonly code: PimErrorCode
  /** Technical detail for logs — never shown to the user. */
  readonly detail: string
  constructor(code: PimErrorCode, detail = '') {
    const human = PIM_HUMAN[code]
    super(`${human.text}（${code}）｜下一步：${human.next}`)
    this.name = 'PimError'
    this.code = code
    this.detail = detail
  }
}

/** Split one CSV line, keeping empty cells and honouring double quotes and "" escapes. */
function splitLine(line: string): string[] {
  const cells: string[] = []
  let cell = ''
  let quoted = false
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i]!
    if (quoted) {
      if (ch === '"' && line[i + 1] === '"') {
        cell += '"'
        i += 1
      } else if (ch === '"') quoted = false
      else cell += ch
    } else if (ch === '"' && cell.trim() === '') quoted = true
    else if (ch === ',') {
      cells.push(cell.trim())
      cell = ''
    } else cell += ch
  }
  cells.push(cell.trim())
  return cells
}
export function gtinValid(raw: string): boolean {
  const digits = raw.replace(/[^0-9]/g, '')
  if (![8, 12, 13, 14].includes(digits.length) || digits !== raw) return false
  const nums = [...digits].map(Number)
  const check = nums.pop()!
  let sum = 0
  for (let i = nums.length - 1, w = 3; i >= 0; i -= 1, w = w === 3 ? 1 : 3) sum += nums[i]! * w
  return (10 - (sum % 10)) % 10 === check
}
export interface GtinInfo {
  gtin: string
  valid: boolean
  format: 'GTIN-8' | 'GTIN-12' | 'GTIN-13' | 'GTIN-14' | 'unknown'
  indicator: number | null
  variable_measure: boolean
}
export function gtinInfo(raw: string): GtinInfo {
  const digits = raw.replace(/[^0-9]/g, '')
  const format = ({ 8: 'GTIN-8', 12: 'GTIN-12', 13: 'GTIN-13', 14: 'GTIN-14' } as const)[digits.length as 8 | 12 | 13 | 14] ?? 'unknown'
  const valid = digits === raw && gtinValid(raw)
  // GS1 General Specifications: for GTIN-14 the leading indicator digit 1-8 marks a packaging
  // level, 9 marks a variable-measure trade item, and 0 is the base unit.
  const indicator = format === 'GTIN-14' && valid ? Number(digits[0]) : null
  return { gtin: raw, valid, format, indicator, variable_measure: indicator === 9 }
}

export function parseCsv(text: string): PimRow[] {
  const lines = text.replace(/^\uFEFF/, '').trim().split(/\r?\n/).filter((line) => line.trim() !== '')
  if (lines.length < 2) throw new PimError('E_PIM_CSV_EMPTY')
  const header = splitLine(lines[0]!).map((h) => h.toLowerCase())
  const idx = (name: string) => header.indexOf(name)
  for (const field of ['sku', 'title', 'gtin', 'price']) if (idx(field) < 0) throw new PimError('E_PIM_HEADER', field)
  return lines.slice(1).map((line, rowIndex) => {
    const cells = splitLine(line)
    // A hand-edited CSV can shift every column after a missing comma; refuse it instead of guessing.
    if (cells.length !== header.length) throw new PimError('E_PIM_CSV_ROW', `row ${rowIndex + 2}: expected ${header.length}, got ${cells.length}`)
    return { sku: cells[idx('sku')] ?? '', title: cells[idx('title')] ?? '', gtin: cells[idx('gtin')] ?? '', price: cells[idx('price')] ?? '' }
  })
}
export function validateRows(rows: PimRow[]): PimIssue[] {
  const issues: PimIssue[] = []
  const seen = new Set<string>()
  const seenGtin = new Set<string>()
  for (const row of rows) {
    const sku = row.sku || '(empty)'
    if (!row.sku) issues.push({ sku, field: 'sku', code: 'E_PIM_SKU_REQUIRED' })
    else if (seen.has(row.sku.toLowerCase())) issues.push({ sku, field: 'sku', code: 'E_PIM_SKU_DUPLICATE' })
    else seen.add(row.sku.toLowerCase())
    if (!row.title) issues.push({ sku, field: 'title', code: 'E_PIM_TITLE_REQUIRED' })
    if (row.gtin && !gtinValid(row.gtin)) issues.push({ sku, field: 'gtin', code: 'E_PIM_GTIN_INVALID' })
    else if (row.gtin) {
      if (seenGtin.has(row.gtin)) issues.push({ sku, field: 'gtin', code: 'E_PIM_GTIN_DUPLICATE' })
      else seenGtin.add(row.gtin)
    }
    const price = Number(row.price)
    if (!row.price || !Number.isFinite(price) || price < 0) issues.push({ sku, field: 'price', code: 'E_PIM_PRICE_INVALID' })
    else if (!/^\d+(\.\d{1,2})?$/.test(row.price.trim())) issues.push({ sku, field: 'price', code: 'E_PIM_PRICE_PRECISION' })
  }
  return issues
}

/**
 * SSCC (Serial Shipping Container Code) check per the GS1 General Specifications: 18 digits,
 * the final digit is the mod-10 check digit computed over the first 17 with weights 3/1 from the right.
 */
export interface SsccResult { sscc: string; valid: boolean; reason?: string }
export function ssccCheck(raw: string): SsccResult {
  const sscc = raw.replace(/\s+/g, '')
  if (!/^\d{18}$/.test(sscc)) return { sscc, valid: false, reason: 'E_PIM_SSCC_FORMAT' }
  const nums = [...sscc].map(Number)
  const check = nums.pop()!
  let sum = 0
  for (let i = nums.length - 1, weight = 3; i >= 0; i -= 1, weight = weight === 3 ? 1 : 3) sum += nums[i]! * weight
  if ((10 - (sum % 10)) % 10 !== check) return { sscc, valid: false, reason: 'E_PIM_SSCC_CHECKSUM' }
  return { sscc, valid: true }
}
