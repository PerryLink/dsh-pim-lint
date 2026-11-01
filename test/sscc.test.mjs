import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'

const tools = Object.fromEntries(createTools().map((t) => [t.name, t]))
const exec = { callId: 'sscc' }

test('a valid SSCC passes the mod-10 check', async () => {
  const r = await tools['pim.sscc_check'].execute({ sscc: '340123450000000017' }, exec)
  assert.equal(r.valid, true)
  assert.equal(r.reason, undefined)
})

test('a wrong check digit and a bad length are distinct', async () => {
  const checksum = await tools['pim.sscc_check'].execute({ sscc: '340123450000000018' }, exec)
  assert.equal(checksum.valid, false)
  assert.equal(checksum.reason, 'E_PIM_SSCC_CHECKSUM')
  const format = await tools['pim.sscc_check'].execute({ sscc: '3401234500000000' }, exec)
  assert.equal(format.valid, false)
  assert.equal(format.reason, 'E_PIM_SSCC_FORMAT')
})

test('spaces are ignored', async () => {
  const r = await tools['pim.sscc_check'].execute({ sscc: '340123450000000017 ' }, exec)
  assert.equal(r.valid, true)
})
