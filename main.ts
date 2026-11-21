// news-image-20261121 — one image summing up Saturday 21 November 2026.
// The picture itself sits beside this file as entry.png, drawn by
// tools/make-image.py from that day's checked news, and this program's
// only job is to hand that exact file to the grader as /output/entry.png.
// Nothing is generated or fetched while it runs, so two runs always write
// the same bytes. It first makes sure the output directory exists, so it
// works in a fresh directory as well as a reused one, and it prints the
// path and size it wrote for the run log. The image file is copied
// byte for byte: the grader sees exactly the entry.png in this repo.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
if (!existsSync(outputDir)) mkdirSync(outputDir, { recursive: true });
const outputPath = join(outputDir, 'entry.png');
copyFileSync(new URL('./entry.png', import.meta.url), outputPath);
console.log(`wrote ${outputPath} (${statSync(outputPath).size} bytes)`);
