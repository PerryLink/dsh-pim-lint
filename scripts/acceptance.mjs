import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import { createTools } from '../lib/plugin/tools.js'

const sha256 = (value) => createHash('sha256').update(value).digest('hex')
const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'pim-acceptance' }
const valid = await tools['pim.validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99' }, exec)
const bad = await tools['pim.validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99\nA,,123,-1' }, exec)
const gtin = await tools['pim.gtin_check'].execute({ gtin: '4006381333931' }, exec)
const structure = await tools['pim.gtin_structure'].execute({ gtin: '94006381333934' }, exec)
const dup = await tools['pim.validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99\nB,Widget 2,4006381333931,12.345' }, exec)
const sscc = await tools['pim.sscc_check'].execute({ sscc: '340123450000000017' }, exec)
const ssccBad = await tools['pim.sscc_check'].execute({ sscc: '340123450000000018' }, exec)
const metrics = [
  { i: 'PIM-A01', m: 'valid catalog accepted', t: '1/1', a: valid.rows === 1 && valid.issues.length === 0 ? 1 : 0, p: valid.rows === 1 && valid.issues.length === 0 },
  { i: 'PIM-A02', m: 'duplicate/bad GTIN/price issues', t: '3', a: bad.issues.length, p: bad.issues.length >= 3 },
  { i: 'PIM-A03', m: 'GTIN check digit', t: '1/1', a: gtin.valid ? 1 : 0, p: gtin.valid === true },
  { i: 'PIM-A04', m: 'GTIN-14 packaging indicator / variable measure', t: '9', a: structure.indicator, p: structure.indicator === 9 && structure.variable_measure === true },
  { i: 'PIM-A05', m: 'duplicate GTIN reported', t: '1', a: dup.issues.filter((x) => x.code === 'E_PIM_GTIN_DUPLICATE').length, p: dup.issues.some((x) => x.code === 'E_PIM_GTIN_DUPLICATE') },
  { i: 'PIM-A06', m: 'over-precise price reported', t: '1', a: dup.issues.filter((x) => x.code === 'E_PIM_PRICE_PRECISION').length, p: dup.issues.some((x) => x.code === 'E_PIM_PRICE_PRECISION') },
  { i: 'PIM-A07', m: 'SSCC mod-10 check', t: '1', a: sscc.valid && ssccBad.reason === 'E_PIM_SSCC_CHECKSUM' ? 1 : 0, p: sscc.valid === true && ssccBad.reason === 'E_PIM_SSCC_CHECKSUM' },
]
for (const row of metrics) if (!row.p) throw new Error(`failed ${row.i}`)

// Evidence JSON is the hash source for every SKU row, so the CSV cannot drift from the run.
const runId = `pim-${new Date().toISOString().replace(/[:.]/g, '-')}`
const evidence = {
  run_id: runId,
  scope: 'PIM-S1',
  status: 'partial',
  counted: false,
  note: 'synthetic catalog; 0 real products',
  metrics,
  pass: metrics.every((row) => row.p),
}
const evidenceText = `${JSON.stringify(evidence, null, 2)}\n`
const evidenceDir = path.join(process.cwd(), 'evidence', runId)
mkdirSync(evidenceDir, { recursive: true })
writeFileSync(path.join(evidenceDir, 'result.json'), evidenceText)
const evidenceHash = sha256(evidenceText)

// PS1-QS01: the shipped quickstart must still reproduce its golden file.
const goldenHash = sha256(readFileSync('samples/quickstart/expected/result.json'))
let quickstartPass = true
try {
  execFileSync(process.execPath, ['samples/quickstart/run.mjs', '--check'], { stdio: 'ignore' })
} catch {
  quickstartPass = false
}

const header = 'req_id,metric,threshold,actual,script,evidence_sha256,pass,source,counted'
const rows = [
  ...metrics.map((row) => `${row.i},${row.m},${row.t},${row.a},scripts/acceptance.mjs,${evidenceHash},${row.p},public/synthetic,false`),
  `PS1-QS01,quickstart 样例与金标一致,1/1,1,scripts/acceptance.mjs,${goldenHash},${quickstartPass},synthetic/quickstart,true`,
]
writeFileSync('ACCEPTANCE.csv', `${header}\n${rows.join('\n')}\n`)
if (!evidence.pass || !quickstartPass) process.exit(1)
console.log(`acceptance ok: ${metrics.length}/${metrics.length} public/synthetic + PS1-QS01 quickstart`)
