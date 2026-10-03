"""Local try-it page for the Viveka engine (owner and testers only; nothing is published).

  python scripts/serve.py            then open http://127.0.0.1:8765

- "Ask": runs the engine with the pass/fail gate, exactly as a user would see it (internal mode:
  drafts are marked DRAFT). Questions are answered in memory and never written anywhere.
- "Add a test case": for the independent test set. Cases written here are saved to
  data/tests/independent.json, deliberately, because they are test data, not user conversations.
  They are scored once on the engine as it stands before anyone tunes against them (tests/README.md).
Listens on 127.0.0.1 only.
"""
import json, sys, threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.core import answer, load_library  # noqa: E402

CASES = ROOT / "data" / "tests" / "independent.json"
LOCK = threading.Lock()

PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Viveka (local)</title>
<style>
:root{--bg:#faf8f4;--fg:#1f1d1a;--mut:#6b655c;--card:#fff;--line:#e6e0d6;--acc:#8a4b14;--warn:#9b1c1c;--warnbg:#fdecec;--ok:#1f6f43;--okbg:#e9f6ef}
@media (prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece7df;--mut:#a39c90;--card:#211e1a;--line:#36312a;--acc:#e0a46a;--warn:#ffb4b4;--warnbg:#3a1d1d;--ok:#9fe0bb;--okbg:#17301f}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:760px;margin:0 auto;padding:24px 16px 64px}h1{font-size:28px;margin:0}.sub{color:var(--mut);margin:4px 0 20px}
nav{display:flex;gap:8px;margin-bottom:16px}nav button{background:none;border:1px solid var(--line);color:var(--fg);padding:8px 14px;border-radius:999px;cursor:pointer}
nav button.on{background:var(--acc);border-color:var(--acc);color:#fff}
textarea,input,select{width:100%;font:inherit;padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--fg)}
textarea{min-height:110px;resize:vertical}.row{display:flex;gap:12px;margin:10px 0}.row>*{flex:1}
.go{background:var(--acc);color:#fff;border:0;border-radius:10px;padding:12px 18px;font:inherit;font-weight:600;cursor:pointer;width:100%}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:12px 0}
.lab{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--mut);margin-bottom:4px}
.draft{background:var(--warnbg);color:var(--warn);border-radius:10px;padding:8px 12px;font-size:14px}
.safety{border-color:var(--warn)}.safety .lab{color:var(--warn)}.prot{border-color:var(--acc)}
.dev{font-family:"Noto Serif Devanagari",serif;font-size:18px;color:var(--mut);margin-top:6px}
ul{margin:6px 0 0;padding-left:20px}.mut{color:var(--mut);font-size:14px}.gate{font-size:13px;color:var(--mut)}
.okmsg{background:var(--okbg);color:var(--ok);border-radius:10px;padding:10px 12px}
h2{font-size:20px;margin:6px 0}
</style></head><body><main>
<h1>Viveka</h1><p class="sub">Local test page. Not published. What you type here is answered in memory and not saved.</p>
<nav><button id="t1" class="on" onclick="tab(1)">Ask</button><button id="t2" onclick="tab(2)">Add a test case</button></nav>
<section id="s1">
<textarea id="q" placeholder="Describe your situation in your own words..."></textarea>
<div class="row"><input id="age" type="number" min="10" max="110" placeholder="Age (optional)"><select id="reg"><option value="IN">Help lines: India</option><option value="US">US</option><option value="UK">UK</option></select></div>
<button class="go" onclick="ask()">Ask Viveka</button><div id="out"></div></section>
<section id="s2" hidden>
<p class="mut">For the independent test set: write a realistic situation the engine has never seen, and say what a good answer must do. Cases are scored once, before anyone tunes against them.</p>
<textarea id="ct" placeholder="The situation, in the person's own words"></textarea>
<div class="row"><select id="cc"><option>adult</option><option>teen</option><option>ambiguous</option><option>hard</option><option>safety</option></select>
<select id="cs"><option value="">Safety route: none</option><option value="support">support (distress)</option><option value="danger">danger (abuse, threats)</option><option value="crisis">crisis (self-harm)</option></select></div>
<textarea id="cg" placeholder="What a good answer must do (and must not do)" style="min-height:80px"></textarea>
<div class="row"><input id="cn" placeholder="Your name or initials (author)"></div>
<button class="go" onclick="addCase()">Save test case</button><div id="cout"></div></section>
</main><script>
function tab(n){for(const i of[1,2]){document.getElementById('s'+i).hidden=i!==n;document.getElementById('t'+i).classList.toggle('on',i===n)}}
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function card(label,html,cls=''){return `<div class="card ${cls}"><div class="lab">${esc(label)}</div>${html}</div>`}
function helps(h){return h&&h.length?'<ul>'+h.map(x=>`<li>${esc(x.name)}: <b>${esc(x.number)}</b> (${esc(x.region)})</li>`).join('')+'</ul>':''}
async function ask(){const q=document.getElementById('q').value.trim();if(!q)return;const o=document.getElementById('out');o.innerHTML='<p class="mut">Thinking...</p>';
const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q,age:document.getElementById('age').value,region:document.getElementById('reg').value})});
const a=await r.json();if(a.error){o.innerHTML=card('Error',esc(a.error));return}let h=`<p class="draft">${esc(a.notice)}</p>`;
if(a.safety)h+=card(a.safety.label+' · safety',`<p>${esc(a.safety.message)}</p>${helps(a.safety.help)}`,'safety');
if(a.protective)h+=card(a.protective.label+' · your health',`<p>${esc(a.protective.text)}</p>${helps(a.protective.help)}`,'prot');
if(a.clarifying_questions&&a.clarifying_questions.length)h+=card('Questions that could change this answer','<ul>'+a.clarifying_questions.map(x=>`<li>${esc(x)}</li>`).join('')+'</ul>');
const rc=a.recommendation;if(rc)h+=card(rc.label+' · recommendation',`<h2>${esc(rc.text)}</h2>${rc.why_it_fits_you?`<p class="mut">${esc(rc.why_it_fits_you)}</p>`:''}${rc.application?`<p>${esc(rc.application)}</p>`:''}`);
for(const s of a.sources||[])h+=card(`Source text · ${s.id}`,`<p>"${esc(s.english)}"</p><div class="dev">${esc(s.devanagari)}</div>`);
const cm=(a.commentary||[]);if(cm.length)h+=card("Commentator's view",cm.map(c=>`<p>${c.note?`<b>${esc(c.commentator)}:</b> ${esc(c.note)}`:`<span class="mut">${esc(c.missing)}</span>`}</p>`).join(''));
if(a.example){const e=a.example;h+=card(e.label,`<p><b>${esc(e.title)}.</b> ${esc(e.event)}</p><p>${esc(e.lesson)}</p><p class="mut">Limits: ${esc(e.limits)}${e.verified?'':' (Not yet verified against its source.)'}</p>`)}
if(a.challenge){const c=a.challenge;h+=card(c.label+' · strongest alternative',`<p>${esc(c.text)}</p><p>"${esc(c.source.english)}" <span class="mut">(${esc(c.source.id)})</span></p><p class="mut">When the recommendation misleads: ${esc(c.when_the_recommendation_misleads)}</p>`)}
if(a.next_step)h+=card(a.next_step.label+' · one next step',`<p><b>${esc(a.next_step.text)}</b></p>`);
if(a.safety_footer)h+=`<p class="mut">${esc(a.safety_footer.text)}</p>`;
h+=`<p class="gate">Gate: ${a.withheld?'withheld':a.clarify?'clarifying question':a.regenerated?'passed after a replacement':'passed'}${(a.gate_log||[]).length?' · tried: '+a.gate_log.map(g=>esc(g.principle)).join(', '):''}</p>`;o.innerHTML=h}
async function addCase(){const b={text:document.getElementById('ct').value.trim(),category:document.getElementById('cc').value,safety:document.getElementById('cs').value||null,good_answer:document.getElementById('cg').value.trim(),author:document.getElementById('cn').value.trim()};
const o=document.getElementById('cout');if(!b.text||!b.good_answer||!b.author){o.innerHTML=card('Missing','Please fill in the situation, what a good answer must do, and the author.');return}
const r=await fetch('/case',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});const a=await r.json();
o.innerHTML=a.error?card('Error',esc(a.error)):`<p class="okmsg">Saved as ${esc(a.id)}. ${esc(a.count)} independent cases so far.</p>`;if(!a.error){document.getElementById('ct').value='';document.getElementById('cg').value=''}}
document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey))ask()});
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # no request logging: questions are never written anywhere
        pass

    def send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send(200, PAGE, "text/html; charset=utf-8")
        else:
            self.send(404, json.dumps({"error": "not found"}))

    def body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(min(n, 20000)) or b"{}")

    def do_POST(self):
        try:
            b = self.body()
            if self.path == "/ask":
                q = str(b.get("q", ""))[:4000]
                profile = {}
                if str(b.get("age", "")).isdigit():
                    profile["age"] = int(b["age"])
                a = answer(q, profile, mode="internal", region=b.get("region") or None)
                a.pop("question", None)
                self.send(200, json.dumps(a, ensure_ascii=False, default=str))
            elif self.path == "/case":
                with LOCK:
                    cases = json.loads(CASES.read_text(encoding="utf-8")) if CASES.exists() else []
                    cid = f"I{len(cases) + 1:03d}"
                    cases.append({"id": cid, "category": b.get("category", "adult"), "text": str(b["text"])[:4000],
                                  "profile": {}, "author": str(b["author"])[:80],
                                  "written": datetime.now().astimezone().isoformat(timespec="minutes"),
                                  "good_answer": str(b["good_answer"])[:4000],
                                  "expect": {"safety": b.get("safety") or None}})
                    CASES.write_text(json.dumps(cases, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
                self.send(200, json.dumps({"id": cid, "count": len(cases)}))
            else:
                self.send(404, json.dumps({"error": "not found"}))
        except Exception as e:  # report, never crash the page
            self.send(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))


def main():
    load_library()
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8765
    print(f"Viveka local page: http://127.0.0.1:{port}  (Ctrl+C to stop)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
