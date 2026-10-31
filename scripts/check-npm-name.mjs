import { execFileSync } from 'node:child_process'
try { execFileSync('npm', ['view', '@perrylink/dsh-pim-lint', 'version', '--registry=https://registry.npmjs.org/'], { stdio: 'ignore' }); console.log('package exists') } catch { console.log('name free') }
