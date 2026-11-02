import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
execFileSync(process.execPath, ['scripts/acceptance.mjs'], { stdio: 'inherit' })
const rows = readFileSync('ACCEPTANCE.csv', 'utf8').trim().split('\n').slice(1).map((row) => row.split(','))
if (rows.length === 0) process.exit(1)
for (const row of rows) {
  if (row.length !== 9 || row[6] !== 'true' || !row[3] || !row[5]) process.exit(1)
}
if (!rows.some((row) => row[0] === 'PS1-QS01')) process.exit(1)
console.log(`gate ok: ${rows.length} rows (${rows.filter((row) => row[7] === 'public/synthetic').length} public/synthetic + PS1-QS01)`)
