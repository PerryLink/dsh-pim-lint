#!/usr/bin/env node
/**
 * dsh-pim-lint quickstart — runs the built plugin tools over the bundled
 * synthetic catalog. The golden file `expected/result.json` is the stdout of
 * `node samples/quickstart/run.mjs --json`, so it is a real run, not hand-written.
 *
 *   node samples/quickstart/run.mjs            # human-readable summary
 *   node samples/quickstart/run.mjs --json     # the golden result on stdout
 *   node samples/quickstart/run.mjs --check    # recompute and diff against the golden file
 */
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createTools } from '../../lib/plugin/tools.js'

const here = path.dirname(fileURLToPath(import.meta.url))
const inputDir = path.join(here, 'input')
const expectedPath = path.join(here, 'expected', 'result.json')
const mode = process.argv.includes('--check') ? 'check' : process.argv.includes('--json') ? 'json' : 'summary'

function parseCsvRows(text) {
  const [header, ...lines] = text.replace(/^\uFEFF/, '').trim().split(/\r?\n/)
  const columns = header.split(',').map((value) => value.trim().toLowerCase())
  return lines.filter((line) => line.trim() !== '').map((line) => {
    const cells = line.split(',').map((value) => value.trim())
    return Object.fromEntries(columns.map((column, index) => [column, cells[index] ?? '']))
  })
}

async function run() {
  const catalogText = await readFile(path.join(inputDir, 'catalog.csv'), 'utf8')
  const codeRows = parseCsvRows(await readFile(path.join(inputDir, 'codes.csv'), 'utf8'))

  const tools = Object.fromEntries(createTools().map((tool) => [tool.name, tool]))
  const call = { callId: 'quickstart' }

  const validated = await tools['pim_validate'].execute({ csv_text: catalogText }, call)

  const counts = new Map()
  for (const issue of validated.issues) counts.set(issue.code, (counts.get(issue.code) ?? 0) + 1)
  const issuesByCode = Object.fromEntries([...counts.entries()].sort(([a], [b]) => a.localeCompare(b)))

  const checks = []
  for (const row of codeRows) {
    const structure = await tools['pim_gtin_structure'].execute({ gtin: row.gtin }, call)
    const sscc = await tools['pim_sscc_check'].execute({ sscc: row.sscc }, call)
    checks.push({
      gtin: structure.gtin,
      format: structure.format,
      gtin_valid: structure.valid,
      packaging_indicator: structure.indicator ?? null,
      variable_measure: structure.variable_measure,
      sscc: sscc.sscc,
      sscc_valid: sscc.valid,
      sscc_reason: sscc.reason ?? null,
    })
  }

  return {
    sample: 'samples/quickstart/input/catalog.csv',
    rows: validated.rows,
    issues: validated.issues.length,
    issues_by_code: issuesByCode,
    issues_detail: validated.issues,
    checks,
  }
}

function summary(result) {
  console.log('dsh-pim-lint quickstart - 合成商品目录（不是真实商品数据）')
  console.log(`读入 ${result.rows} 行，发现 ${result.issues} 个问题`)
  for (const issue of result.issues_detail) console.log(`  ${issue.sku} / ${issue.field} / ${issue.code}`)
  for (const check of result.checks) {
    const structure = check.format === 'GTIN-14'
      ? `GTIN-14 指示位 ${check.packaging_indicator}${check.variable_measure ? '（变量度量）' : ''}`
      : `${check.format}`
    console.log(`GTIN ${check.gtin} -> ${structure}，校验${check.gtin_valid ? '通过' : '失败（E_PIM_GTIN_INVALID）'}`)
    console.log(`SSCC ${check.sscc} -> ${check.sscc_valid ? '校验通过' : `校验失败（${check.sscc_reason}）`}`)
  }
}

const result = await run()

if (mode === 'json') {
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
} else if (mode === 'check') {
  const expected = JSON.parse(await readFile(expectedPath, 'utf8'))
  assert.deepEqual(result, expected)
  summary(result)
  console.log('golden samples/quickstart/expected/result.json matches')
  console.log('quickstart ok')
} else {
  summary(result)
  console.log('run with --check to compare against expected/result.json')
}
