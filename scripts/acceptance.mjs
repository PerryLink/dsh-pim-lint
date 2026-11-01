import { writeFileSync } from 'node:fs'
import { createTools } from '../lib/plugin/tools.js'
const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'pim-acceptance' }
const valid = await tools['pim.validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99' }, exec)
const bad = await tools['pim.validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99\nA,,123,-1' }, exec)
const gtin = await tools['pim.gtin_check'].execute({ gtin: '4006381333931' }, exec)
const structure = await tools['pim.gtin_structure'].execute({ gtin: '94006381333934' }, exec)
const dup = await tools['pim.validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99\nB,Widget 2,4006381333931,12.345' }, exec)
const rows = [
  { req_id: 'PIM-A01', metric: 'valid catalog accepted', actual: valid.rows === 1 && valid.issues.length === 0, expected: true },
  { req_id: 'PIM-A02', metric: 'duplicate/bad GTIN/price issues', actual: bad.issues.length >= 3, expected: true },
  { req_id: 'PIM-A03', metric: 'GTIN check digit', actual: gtin.valid, expected: true },
  { req_id: 'PIM-A04', metric: 'GTIN-14 packaging indicator / variable measure', actual: structure.indicator === 9 && structure.variable_measure === true, expected: true },
  { req_id: 'PIM-A05', metric: 'duplicate GTIN reported', actual: dup.issues.some((i) => i.code === 'E_PIM_GTIN_DUPLICATE'), expected: true },
  { req_id: 'PIM-A06', metric: 'over-precise price reported', actual: dup.issues.some((i) => i.code === 'E_PIM_PRICE_PRECISION'), expected: true },
]
for (const row of rows) if (row.actual !== row.expected) throw new Error(`failed ${row.req_id}`)
const csv = ['req_id,metric,actual,pass,source,counted', ...rows.map((r) => `${r.req_id},${r.metric},${r.actual},true,public/synthetic,false`)].join('\n') + '\n'
writeFileSync('ACCEPTANCE.csv', csv)
console.log('acceptance ok: 6/6 public/synthetic')
