import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'
const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'pim' }
test('valid catalog', async () => {
  const r = await tools['pim.validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99' }, exec)
  assert.equal(r.rows, 1); assert.equal(r.issues.length, 0)
})
test('duplicate / bad GTIN / bad price', async () => {
  const r = await tools['pim.validate'].execute({ csv_text: 'sku,title,gtin,price\nA,Widget,4006381333931,9.99\nA,,123,-1' }, exec)
  assert.ok(r.issues.some((i) => i.code === 'E_PIM_SKU_DUPLICATE'))
  assert.ok(r.issues.some((i) => i.code === 'E_PIM_GTIN_INVALID'))
  assert.ok(r.issues.some((i) => i.code === 'E_PIM_PRICE_INVALID'))
})
test('gtin check', async () => {
  assert.equal((await tools['pim.gtin_check'].execute({ gtin: '4006381333931' }, exec)).valid, true)
  assert.equal((await tools['pim.gtin_check'].execute({ gtin: '4006381333932' }, exec)).valid, false)
})
