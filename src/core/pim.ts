export interface PimRow { sku: string; title: string; gtin: string; price: string }
export interface PimIssue { sku: string; field: string; code: string }
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
  const lines = text.trim().split(/\r?\n/).filter(Boolean)
  if (lines.length < 2) throw new Error('E_PIM_CSV_EMPTY')
  const header = lines[0]!.split(',').map((h) => h.trim().toLowerCase())
  const idx = (name: string) => header.indexOf(name)
  for (const field of ['sku', 'title', 'gtin', 'price']) if (idx(field) < 0) throw new Error(`E_PIM_HEADER: ${field}`)
  return lines.slice(1).map((line) => {
    const cells = line.match(/(".*?"|[^,]+)(?=,|$)/g)?.map((v) => v.replace(/^"|"$/g, '').trim()) ?? []
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
