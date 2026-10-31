import type { Context } from '@deepseek-ai/cordis'
import { createTools } from './tools.js'
export const name = 'dsh-pim-lint'
export const inject = ['tools']
export async function apply(ctx: Context): Promise<void> {
  for (const tool of createTools()) ctx.tools.register(tool)
}
