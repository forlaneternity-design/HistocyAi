// Build gate: fails the workflow if the app would start blank.
const fs = require('fs'), c = require('crypto');
const f = process.argv[2] || 'index.html';
const s = fs.readFileSync(f, 'utf8');
let bad = 0;
const fail = (m) => { console.error('FAIL: ' + m); bad++; };
const meta = (s.match(/<meta[^>]*http-equiv=["']Content-Security-Policy["'][^>]*>/i) || [''])[0];
if (!meta) fail('no CSP meta tag found');
const csp = (meta.match(/script-src[^;"]*/) || [''])[0];
if (!csp) fail('no script-src in the CSP meta tag');
if (!/charset/i.test(s.slice(0, 1024))) fail('no charset declaration in the first 1024 bytes');
const re = /<script>([\s\S]*?)<\/script>/g;
let m, n = 0;
while ((m = re.exec(s))) {
  n++;
  try { new Function(m[1]); } catch (e) { fail('script ' + n + ' does not parse: ' + e.message); }
  if (!csp.includes('unsafe-inline')) {
    const h = "'sha256-" + c.createHash('sha256').update(m[1], 'utf8').digest('base64') + "'";
    if (!csp.includes(h)) fail('script ' + n + ' hash missing from CSP');
  }
}
if (!n) fail('no inline scripts found');
const hd = s.match(/<[a-zA-Z][^<>]{0,300}?\son[a-z]+\s*=/g) || [];
if (hd.length && !csp.includes('unsafe-inline')) fail(hd.length + ' inline handlers would be blocked by CSP');
console.log(n + ' inline scripts checked. script-src: ' + csp.slice(0, 70) + '...');
process.exit(bad ? 1 : 0);
