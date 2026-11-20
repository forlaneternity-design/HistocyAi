"""Idempotent v5.0.2 hardening for the single-file Cytovision app.
Usage: python3 scripts/harden.py index.html
Always regenerates script-src sha256 hashes from the current inline scripts.
RUO prototype tooling; does not change any clinical logic."""
import re, hashlib, base64, sys

p = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = open(p, encoding='utf8').read()
MARK = 'v5.0.2 (Nov 2026)'

GUARD = """<script>(function(){var m=[];try{if(!window.Promise)m.push('Promise');if(!window.fetch)m.push('fetch');if(!window.indexedDB)m.push('IndexedDB');if(!Object.entries)m.push('Object.entries');}catch(x){}
var done=false;function show(w){if(done||!document.body)return;done=true;var d=document.createElement('div');d.setAttribute('role','alert');d.style.cssText='position:fixed;top:0;left:0;right:0;bottom:0;z-index:99999;background:#fff;color:#111;padding:24px;font:16px/1.5 sans-serif;overflow:auto';d.innerHTML='<h2>This browser is too old</h2><p>Cytovision needs a newer browser engine. On Android, update <b>Android System WebView</b> and <b>Chrome</b> in Google Play, then reopen the app.</p><p style="font-size:13px;color:#555">'+w+'</p>';document.body.appendChild(d);}
if(m.length)document.addEventListener('DOMContentLoaded',function(){show('Missing: '+m.join(', '));});
window.addEventListener('error',function(e){if(/SyntaxError|Unexpected (token|identifier|reserved)/.test(String(e&&e.message))){if(document.body)show('Script could not start (engine too old).');else document.addEventListener('DOMContentLoaded',function(){show('Script could not start (engine too old).');});}});})();</script>
"""

A11Y = """<script>(function(){'use strict';
window.addEventListener('click',function(e){var t=e.target&&e.target.closest?e.target.closest('[data-ins-tab],[data-review-tab]'):null;if(!t||typeof S==='undefined')return;if(t.dataset.insTab)S.insTab=t.dataset.insTab;if(t.dataset.reviewTab)S.reviewTab=t.dataset.reviewTab;},true);
var opener=null;
if(typeof openSheet==='function'){var os=openSheet;openSheet=function(){opener=document.activeElement;var r=os.apply(this,arguments);setTimeout(function(){var d=document.querySelector('#sheetHost [role=dialog]');if(d&&!d.contains(document.activeElement)){d.setAttribute('tabindex','-1');d.focus();}},0);return r;};}
if(typeof closeSheet==='function'){var cs=closeSheet;closeSheet=function(silent){var r=cs.apply(this,arguments);if(!silent&&opener&&opener.focus&&document.contains(opener)){try{opener.focus();}catch(x){}}if(!silent)opener=null;return r;};}
document.addEventListener('keydown',function(e){var d=document.querySelector('#sheetHost [role=dialog]');if(!d)return;if(e.key==='Escape'){e.preventDefault();if(typeof closeSheet==='function')closeSheet();return;}if(e.key!=='Tab')return;var f=d.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]):not([type=hidden]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])');if(!f.length)return;var a=f[0],z=f[f.length-1],c=document.activeElement;if(e.shiftKey&&(c===a||c===d)){e.preventDefault();z.focus();}else if(!e.shiftKey&&c===z){e.preventDefault();a.focus();}});
})();</script>
"""

SC = r'<script>([\s\S]*?)</script>'
if MARK not in s:
    s = re.sub(r'onclick="S\.insTab=\'(\w+)\'"', r'data-ins-tab="\1"', s)
    s = re.sub(r'onclick="S\.reviewTab=\'(\w+)\'"', r'data-review-tab="\1"', s)
    s = re.sub(r'font-size:\s*(?:7|8|9|10|10\.5|11|11\.5)px', 'font-size:12px', s)
    sc = list(re.finditer(SC, s))
    last, first = sc[-1].end(), sc[0].start()
    s = s[:last] + '\n' + A11Y + s[last:]
    s = s[:first] + GUARD + s[first:]
    s = s.replace('<!-- v5.0.1 pilot-hardening changelog',
                  '<!-- ' + MARK + ': tab handlers -> data attributes; hashed script-src; old-WebView guard; sheet Esc/focus-trap; min font 12px.\n     v5.0.1 pilot-hardening changelog', 1)
    print('hardening applied')
else:
    print('already hardened; only refreshing CSP hashes')


MARK2 = 'v5.0.3 (Nov 2026)'
EXTRA = """<script>(function(){'use strict';
var st=document.createElement('style');st.textContent='@media (pointer:coarse){.btn,.btn.sm,button.icon,select,input:not([type=checkbox]):not([type=radio]):not([type=range]){min-height:44px}}#cvOffline{position:fixed;top:0;left:0;right:0;z-index:99998;padding:6px 12px;background:#fff3cd;color:#5c3b00;font:600 13px/1.4 sans-serif;text-align:center;border-bottom:2px solid #5c3b00}@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important}}';document.head.appendChild(st);
var ob=document.createElement('div');ob.id='cvOffline';ob.setAttribute('role','status');ob.hidden=true;ob.textContent='\u26a0 Offline: work is kept on this device. Sync resumes when you reconnect.';document.body.appendChild(ob);
function net(){ob.hidden=navigator.onLine!==false;}window.addEventListener('online',net);window.addEventListener('offline',net);net();
var lt=0;function lab(){lt=0;try{var n=document.querySelectorAll('input,select,textarea,button');for(var i=0;i<n.length;i++){var e=n[i];if(e.type==='hidden'||e.getAttribute('aria-label')||e.getAttribute('aria-labelledby')||e.closest('label'))continue;if(e.tagName==='BUTTON'){if(!e.textContent.trim()&&e.title)e.setAttribute('aria-label',e.title);continue;}if(e.id&&document.querySelector('label[for="'+e.id+'"]'))continue;e.setAttribute('aria-label',e.getAttribute('placeholder')||e.title||e.name||e.id||e.type);}}catch(x){}}
new MutationObserver(function(){if(!lt)lt=requestAnimationFrame(lab);}).observe(document.body,{childList:true,subtree:true});lab();
if(typeof renderNav==='function'){var rn=renderNav;renderNav=function(){rn.apply(this,arguments);var t=document.getElementById('tabs');if(!t)return;var b=[].slice.call(t.children);if(b.length<=5)return;var cur=false,bad=false;window.__cvMore=[];b.forEach(function(x,i){if(i<4)return;x.style.display='none';var sp=x.querySelector('span');window.__cvMore.push({v:x.getAttribute('data-v'),l:sp?sp.textContent:x.getAttribute('data-v')});if(x.getAttribute('aria-current'))cur=true;if(x.querySelector('.badge-dot'))bad=true;});var m=document.createElement('button');m.setAttribute('data-more','1');m.setAttribute('aria-haspopup','dialog');if(cur)m.setAttribute('aria-current','page');m.innerHTML=(typeof icon==='function'?icon('list'):'')+'<span>More'+(bad?' !':'')+'</span>';t.appendChild(m);};
if(document.getElementById('tabs')&&document.getElementById('tabs').children.length)renderNav();}
window.addEventListener('click',function(e){var T=e.target;var m=T.closest&&T.closest('[data-more]');if(m&&window.__cvMore&&typeof openSheet==='function'){e.preventDefault();e.stopPropagation();openSheet({title:'More',html:'<div style="display:grid;gap:8px">'+window.__cvMore.map(function(r){return '<button class="btn" data-act="go" data-v="'+esc(r.v)+'" data-more-go="1">'+esc(r.l)+'</button>';}).join('')+'</div><p style="margin-top:12px;font-size:12px">Cytovision v5.0.3 \u00b7 research use only \u00b7 not for diagnosis</p>'});return;}if(T.closest&&T.closest('[data-more-go]'))setTimeout(function(){if(typeof closeSheet==='function')closeSheet(true);},0);},true);
if('serviceWorker' in navigator&&/^https?:$/.test(location.protocol)){var lk=document.createElement('link');lk.rel='manifest';lk.href='manifest.webmanifest';document.head.appendChild(lk);navigator.serviceWorker.register('sw.js').catch(function(){});}
})();</script>
"""
if MARK2 not in s:
    s, nesc = re.subn(r'(data-[a-z-]+)="\$\{([\w.]*\bid)\}"', r'\1="${esc(\2)}"', s)
    sc = list(re.finditer(SC, s))
    s = s[:sc[-1].end()] + '\n' + EXTRA + s[sc[-1].end():]
    s = s.replace('<!-- ' + MARK, '<!-- ' + MARK2 + ': esc() on data-id attributes, offline banner, auto-labels, 44px taps, More tab (max 5), service worker.\n     ' + MARK, 1)
    print('v5.0.3 extras applied; esc-wrapped attributes:', nesc)

left = re.findall(r'<[a-zA-Z][^<>]{0,300}?\son[a-z]+\s*=', s)
hashes = ' '.join("'sha256-%s'" % base64.b64encode(hashlib.sha256(m.group(1).encode('utf8')).digest()).decode()
                  for m in re.finditer(SC, s))

# In the Android/Capacitor app the SW is not wanted (the app is already offline) and can blank the screen:
# skip registering there, and remove any SW/cache left by an earlier build.
SW_OLD = "if('serviceWorker' in navigator&&/^https?:$/.test(location.protocol)){var lk="
SW_NEW = ("var nat=!!window.Capacitor||/; wv\\)/.test(navigator.userAgent)||location.hostname==='localhost';"
          "if('serviceWorker' in navigator&&nat){navigator.serviceWorker.getRegistrations().then(function(r){r.forEach(function(x){x.unregister();});});"
          "if(window.caches)caches.keys().then(function(k){k.forEach(function(n){caches.delete(n);});});}"
          "if('serviceWorker' in navigator&&!nat&&/^https?:$/.test(location.protocol)){var lk=")
if SW_OLD in s:
    s = s.replace(SW_OLD, SW_NEW)
    print('service worker disabled inside the Android app')


# ---- stage 4 (v5.0.4): TF.js integrity, 14px body text, contrast >= 4.5:1 in every theme ----
SRI_OLD = "s.src=srcs[i++];s.onload="
SRI_NEW = ("s.src=srcs[i++];if(s.src.indexOf('cdn.jsdelivr.net')>-1){s.integrity='sha384-h/XNDFVVo8fubLoOyBCXZW8B+OPOs7cpygLoTtS6f8DDTPRPCoFNMaE4JXtqrSWj';"
           "s.crossOrigin='anonymous';}s.onload=")
if SRI_OLD in s:
    s = s.replace(SRI_OLD, SRI_NEW)
    print('TF.js CDN load now carries an integrity hash (tfjs 4.15.0)')
FONT_ANCHOR = '#cvOffline{position:fixed'
if FONT_ANCHOR in s and 'body{font-size:max(14px' not in s:
    s = s.replace(FONT_ANCHOR, 'body{font-size:max(14px,1rem)}' + FONT_ANCHOR, 1)
    print('body text minimum 14px')

def _lum(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])

def _cr(a, b):
    x, y = sorted([_lum(a), _lum(b)], reverse=True)
    return (x + .05) / (y + .05)

def _step(fg, bg):
    c = [int(fg.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    c = [round(v * .96) for v in c] if _lum(fg) < _lum(bg) else [round(v + (255 - v) * .04) for v in c]
    return '#%02x%02x%02x' % tuple(c)

_PAIRS = [('ink', 'bg'), ('ink', 'surface'), ('ink', 'surface2'), ('ink2', 'bg'), ('ink2', 'surface'),
          ('ink2', 'surface2'), ('hema-ink', 'hema'), ('hema', 'surface'), ('hema', 'hema-soft'),
          ('eosin', 'surface'), ('eosin', 'eosin-soft'), ('og', 'surface'), ('og', 'og-soft'),
          ('lg', 'surface'), ('lg', 'lg-soft'), ('ink', 'hema-soft')]
_fixed = [0]

def _fix_theme(m):
    blk = m.group(0)
    v = dict(re.findall(r'--([\w-]+):\s*(#[0-9a-fA-F]{6})\b', blk))
    if '--bg' not in blk or not v:
        return blk
    old = dict(v)
    for _ in range(3):
        for a, b in _PAIRS:
            if a in v and b in v:
                n = 0
                while _cr(v[a], v[b]) < 4.6 and n < 60:
                    v[a] = _step(v[a], v[b]); n += 1
    for k in v:
        if v[k] != old[k]:
            blk = re.sub(r'(--%s:\s*)#[0-9a-fA-F]{6}\b' % re.escape(k), lambda mm: mm.group(1) + v[k], blk, count=1)
            _fixed[0] += 1
    return blk

s = re.sub(r'(?::root(?:\[data-theme="\w+"\]|:not\(\[data-theme="\w+"\]\))?|\[data-theme="\w+"\])\s*\{[^}]*--bg:[^}]*\}', _fix_theme, s)
if _fixed[0]:
    print('contrast: adjusted %d colour variables to reach 4.5:1' % _fixed[0])


# ---- stage 5 (v5.1): "Midnight lab" theme layer (colours, glow cards, compact tab bar). CSS only. ----
THEME = r"""<style id="cv-theme">
html:root,html:root[data-theme="light"],html:root[data-theme="dark"],html:root:not([data-theme="light"]){
--bg:#070d17;--surface:#0f1a2b;--surface2:#16253b;--ink:#eaf3ff;--ink2:#9db2c9;--line:#1f3550;
--hema:#22d3ee;--hema-ink:#041c24;--hema-soft:#0e3445;
--eosin:#ff8ba7;--eosin-soft:#4a2233;--og:#fbbf5b;--og-soft:#463517;--lg:#4ade9b;--lg-soft:#12402f;
--shadow:0 0 0 1px rgba(34,211,238,.05),0 8px 24px rgba(0,0,0,.4);--nav-h:56px;color-scheme:dark}
body{background:radial-gradient(120% 55% at 10% -10%,rgba(34,211,238,.16),transparent 60%),radial-gradient(90% 45% at 100% 0,rgba(99,102,241,.15),transparent 55%),var(--bg);background-attachment:fixed;color:var(--ink)}
.topbar,header{background:transparent;border-bottom:1px solid var(--line)}
.brand-name,.brand{color:var(--hema)}
.card{border-radius:16px;border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(255,255,255,0)),var(--surface);box-shadow:var(--shadow)}
.btn{border-radius:12px}
.btn.primary,.btn.cv-primary{background:var(--hema);color:var(--hema-ink);box-shadow:0 0 18px rgba(34,211,238,.3)}
.chip,.cv-status-pill,.seg{border-color:var(--line)}
#tabs{background:rgba(8,14,25,.94);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);border-top:1px solid var(--line)}
#tabs button{gap:0}
#tabs button svg{width:22px;height:22px}
#tabs button:not([aria-current]) span:not(.badge-dot){position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
#tabs button[aria-current]{color:var(--hema)}
#tabs button[aria-current] svg{filter:drop-shadow(0 0 6px rgba(34,211,238,.6))}
#tabs button[aria-current]::before{height:2px}
</style>
"""
THEME = re.sub(r'(?::root(?:\[data-theme="\w+"\]|:not\(\[data-theme="\w+"\]\))?|\[data-theme="\w+"\])\s*\{[^}]*--bg:[^}]*\}', _fix_theme, THEME)
s = re.sub(r'<style id="cv-theme">[\s\S]*?</style>\n?', '', s)
_first = re.search(SC, s)
s = s[:_first.start()] + THEME + s[_first.start():]
print('Midnight lab theme layer applied')

if 'charset' not in s[:1024].lower():
    s = re.sub(r'(?i)<!doctype html>', '<!doctype html>\n<meta charset="utf-8">', s, count=1)
mm = re.search(r'<meta[^>]*http-equiv=["\']Content-Security-Policy["\'][^>]*>', s, re.I)
if not mm:
    sys.exit('no CSP meta tag found')
ms = re.search(r"script-src[^;\"]*", mm.group(0))
if not ms:
    sys.exit('no script-src in the CSP meta tag')
class _M:  # span of script-src inside the real CSP meta tag (not comments)
    def start(self): return mm.start() + ms.start()
    def end(self): return mm.start() + ms.end()
m = _M()
hashes = ' '.join("'sha256-%s'" % base64.b64encode(hashlib.sha256(x.group(1).encode('utf8')).digest()).decode()
                  for x in re.finditer(SC, s))  # recompute after all edits
if left:
    print('WARNING: %d inline handlers remain; leaving CSP as is' % len(left))
else:
    s = s[:m.start()] + "script-src 'self' " + hashes + ' https://cdn.jsdelivr.net' + s[m.end():]
    print('CSP script-src refreshed with', hashes.count('sha256-'), 'hashes')
open(p, 'w', encoding='utf8').write(s)
