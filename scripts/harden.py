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
m = re.search(r"script-src[^;\"]*", s)
if not m:
    sys.exit('no script-src found in CSP')
if left:
    print('WARNING: %d inline handlers remain; leaving CSP as is' % len(left))
else:
    s = s[:m.start()] + "script-src 'self' " + hashes + ' https://cdn.jsdelivr.net' + s[m.end():]
    print('CSP script-src refreshed with', hashes.count('sha256-'), 'hashes')
open(p, 'w', encoding='utf8').write(s)
