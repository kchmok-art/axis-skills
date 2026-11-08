#!/usr/bin/env python3
"""axis:ppt3 덱 검증·내보내기 (헤드리스 Chrome)

  python export.py check "덱.html"                       # node --check + 런타임 오류 + 장 수·차트·도식·편집 블록 점검
  python export.py shot  "덱.html" [--slides 1,5,12] [--out DIR] [--block-cdnjs]
                                                        # 장별 스크린샷 (등장 애니메이션 완료 상태로 고정). --slides 없으면 전 장
  python export.py pdf   "덱.html" [--out FILE]          # 인쇄 CSS 로 PDF (슬라이드 1장 = 1쪽)
  python export.py overflow "덱.html"                    # 장마다 1600×900 스테이지 밖으로 넘친 요소를 찾는다

주의
- GPU 를 끄지 않는다(--disable-gpu 는 3D 카드·캔버스를 비워 오판하게 만든다).
- 헤드리스에서는 애니메이션 시계가 진행되지 않으므로 스크린샷은 등장 애니메이션을 완료 상태로 고정한 사본으로 찍는다.
- 장 번호는 1부터. 덱의 해시는 #3 처럼 숫자만 쓴다.
"""
import html, os, re, subprocess, sys, tempfile, urllib.parse

sys.stdout.reconfigure(encoding="utf-8")
CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
]
CLAMP = ('<style>.slide.active .r{animation-duration:.001s!important;animation-delay:0s!important}'
         '.slide{transition-duration:.001s!important}'
         '.fcube,.hcube,.ring,.pulse,.floaty,.pill i,.circuit path,.blob{animation:none!important}'
         '.ill .draw{animation:none!important;stroke-dashoffset:0!important}</style>')
TRAP = '<script>window.__errs=[];addEventListener("error",e=>window.__errs.push(e.message+" @"+e.lineno+":"+e.colno));</script>'


def chrome():
    for p in CANDIDATES:
        if os.path.isfile(p):
            return p
    sys.exit("Chrome/Edge 실행 파일을 찾지 못했습니다. CANDIDATES 에 경로를 추가하세요.")


def file_url(p):
    p = os.path.realpath(p).replace("\\", "/")
    return "file:///" + urllib.parse.quote(p, safe="/:")


def profile():
    return "--user-data-dir=" + os.path.join(tempfile.gettempdir(), "axis-chrome-profile")


def run(args, timeout=120):
    subprocess.run([chrome(), "--headless=new", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check", profile()] + args,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)


def dump(url, budget=10000, extra=()):
    r = subprocess.run([chrome(), "--headless=new", "--no-first-run", "--window-size=1600,900", profile(),
                        f"--virtual-time-budget={budget}", *extra, "--dump-dom", url], capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


def with_injection(src, head_extra="", body_extra=""):
    s = open(src, encoding="utf-8").read()
    # 사본은 임시 폴더에서 열린다 — 덱이 상대 경로로 부르는 사진(1.jpg 등)이 깨지지 않게 원본 폴더를 base 로 건다
    head_extra = '<base href="' + file_url(os.path.dirname(os.path.realpath(src))) + '/">' + head_extra
    if head_extra:
        s = s.replace("</head>", head_extra + "</head>", 1)
    if body_extra:
        s = s.replace("</body>", body_extra + "</body>", 1)
    d = tempfile.mkdtemp(prefix="axis-")
    p = os.path.join(d, os.path.basename(src))
    open(p, "w", encoding="utf-8").write(s)
    return p


def probe_result(out):
    m = re.search(r'<div id="dbg">([^<]*)</div>', out)
    return html.unescape(m.group(1)) if m else None


def cmd_check(src):
    s = open(src, encoding="utf-8").read()
    blocks = re.findall(r"<script(?: data-editor)?>(.*?)</script>", s, re.S)
    js = "\n;\n".join("(function(){" + b + "\n})();" for b in blocks)
    jp = os.path.join(tempfile.gettempdir(), "axis-check.js")
    open(jp, "w", encoding="utf-8").write(js)
    r = subprocess.run(["node", "--check", jp], capture_output=True, text=True)
    print("node --check:", "OK" if r.returncode == 0 else "FAIL\n" + r.stderr)
    n = s.count('<section class="slide')
    print("slides:", n, "| data-editor:", len(re.findall(r"<(style|span|script)[^>]* data-editor(?:=\"\")?>", s)), "(4)",
          "| id=edit:", s.count('id="edit"'), "| id=final:", s.count('id="final"'),
          "| dg:", s.count('class="dg"'), "| canvas[data-chart]:", len(re.findall(r'canvas data-chart=', s)))
    # 모든 장을 한 번씩 열어 차트 생성·도식 렌더까지 돌린 뒤 오류를 모은다
    probe = ('<script>setTimeout(async()=>{const total=document.querySelectorAll(".slide").length;'
             'for(let i=0;i<total;i++){go(i);await new Promise(r=>setTimeout(r,120))}'
             'const d=document.createElement("div");d.id="dbg";'
             'd.textContent="ERRS="+window.__errs.join(" | ")+" | CHART="+(typeof Chart)+" | CHARTS_MADE="+Object.keys(made).length'
             '+" | WIRES="+document.querySelectorAll(".dg-wire svg path:not(.dg-hit)").length+" | EDIT="+(typeof window.__deckHtml);'
             'document.body.appendChild(d);},1500);</script>')
    p = with_injection(src, TRAP, probe)
    print("runtime:", probe_result(dump(file_url(p), 20000)) or "no result (페이지 로드 실패?)")


def cmd_overflow(src):
    probe = ('<script>setTimeout(async()=>{const total=document.querySelectorAll(".slide").length,bad=[];'
             'const st=document.getElementById("stage");'
             'for(let i=0;i<total;i++){go(i);await new Promise(r=>setTimeout(r,150));'
             'const sb=st.getBoundingClientRect(),k=sb.width/1600;'
             'const sl=document.querySelectorAll(".slide")[i];'
             'sl.querySelectorAll("*").forEach(el=>{if(el.closest(".dg-wire")||el.tagName==="CANVAS"||el.tagName==="svg"&&el.closest(".dg"))return;'
             'const r=el.getBoundingClientRect();if(!r.width||!r.height)return;'
             'const b=(r.bottom-sb.top)/k,rt=(r.right-sb.left)/k,l=(r.left-sb.left)/k;'
             'if(b>840||rt>1604||l<-4)bad.push((i+1)+":"+el.tagName.toLowerCase()+(el.className&&typeof el.className==="string"?"."+el.className.split(" ")[0]:"")+" b="+Math.round(b)+" r="+Math.round(rt))});'
             '}const d=document.createElement("div");d.id="dbg";d.textContent=bad.length?bad.slice(0,60).join(" || "):"OK";document.body.appendChild(d);},1500);</script>')
    p = with_injection(src, CLAMP + TRAP, probe)
    print("overflow (밴드 하단 한계 840px 기준):", probe_result(dump(file_url(p), 25000)) or "no result")


def cmd_shot(src, out_dir=None, block_cdnjs=False, slides=None):
    out_dir = os.path.realpath(out_dir or os.path.dirname(os.path.realpath(src)))
    os.makedirs(out_dir, exist_ok=True)
    s = open(src, encoding="utf-8").read()
    total = s.count('<section class="slide')
    nums = slides or list(range(1, total + 1))
    p = with_injection(src, CLAMP)
    extra = ["--host-resolver-rules=MAP cdnjs.cloudflare.com 127.0.0.1"] if block_cdnjs else []
    base = os.path.splitext(os.path.basename(src))[0]
    if not base.isascii():
        base = "slide"   # 헤드리스 Chrome 은 --screenshot 경로의 비ASCII 글자를 못 쓴다
    for n in nums:
        png = os.path.join(out_dir, f"{base}_{n:02d}.png")
        run(["--window-size=1600,900", "--virtual-time-budget=12000", *extra, f"--screenshot={png}", file_url(p) + f"#{n}"])
        print("screenshot:", png)


def cmd_pdf(src, out=None):
    out = out or os.path.splitext(os.path.realpath(src))[0] + ".pdf"
    run(["--window-size=1600,900", "--virtual-time-budget=15000", "--no-pdf-header-footer", f"--print-to-pdf={out}", file_url(src)], timeout=180)
    print("pdf:", out)


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__); return
    cmd, src, opts = a[0], a[1], a[2:]
    out = opts[opts.index("--out") + 1] if "--out" in opts else None
    slides = None
    if "--slides" in opts:
        slides = [int(x) for x in opts[opts.index("--slides") + 1].split(",") if x.strip()]
    if cmd == "check": cmd_check(src)
    elif cmd == "shot": cmd_shot(src, out, "--block-cdnjs" in opts, slides)
    elif cmd == "pdf": cmd_pdf(src, out)
    elif cmd == "overflow": cmd_overflow(src)
    else: print(__doc__)


if __name__ == "__main__":
    main()
