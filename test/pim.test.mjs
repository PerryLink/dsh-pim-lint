import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'
const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'pim' }
test('valid catalog', async () => {
  const r = await tools['pim_validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99' }, exec)
  assert.equal(r.rows, 1); assert.equal(r.issues.length, 0)
})
test('duplicate / bad GTIN / bad price', async () => {
  const r = await tools['pim_validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99\nA,,123,-1' }, exec)
  assert.ok(r.issues.some((i) => i.code === 'E_PIM_SKU_DUPLICATE'))
  assert.ok(r.issues.some((i) => i.code === 'E_PIM_GTIN_INVALID'))
  assert.ok(r.issues.some((i) => i.code === 'E_PIM_PRICE_INVALID'))
})
test('gtin check', async () => {
  assert.equal((await tools['pim_gtin_check'].execute({ gtin: '4006381333931' }, exec)).valid, true)
  assert.equal((await tools['pim_gtin_check'].execute({ gtin: '4006381333932' }, exec)).valid, false)
})

test('GTIN-14 structure carries indicator and variable-measure flag', async () => {
  const variable = await tools['pim_gtin_structure'].execute({ gtin: '94006381333934' }, exec)
  assert.equal(variable.valid, true)
  assert.equal(variable.format, 'GTIN-14')
  assert.equal(variable.indicator, 9)
  assert.equal(variable.variable_measure, true)
  const pack = await tools['pim_gtin_structure'].execute({ gtin: '14006381333938' }, exec)
  assert.equal(pack.indicator, 1)
  assert.equal(pack.variable_measure, false)
  const ean = await tools['pim_gtin_structure'].execute({ gtin: '4006381333931' }, exec)
  assert.equal(ean.format, 'GTIN-13')
  assert.equal(ean.indicator, undefined)
  const bad = await tools['pim_gtin_structure'].execute({ gtin: '4006381333932' }, exec)
  assert.equal(bad.valid, false)
  assert.equal(bad.format, 'GTIN-13')
  assert.equal(bad.indicator, undefined)
})

test('duplicate GTIN and over-precise price are reported', async () => {
  const r = await tools['pim_validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99\nB,Widget 2,4006381333931,12.345' }, exec)
  assert.ok(r.issues.some((i) => i.code === 'E_PIM_GTIN_DUPLICATE' && i.sku === 'B'))
  assert.ok(r.issues.some((i) => i.code === 'E_PIM_PRICE_PRECISION' && i.sku === 'B'))
  assert.equal(r.issues.filter((i) => i.code === 'E_PIM_GTIN_DUPLICATE').length, 1)
})
