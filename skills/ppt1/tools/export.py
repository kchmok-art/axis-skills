#!/usr/bin/env python3
"""axis ppt 덱 검증·내보내기 도구 (헤드리스 Chrome)

  python export.py check "덱.html"                 # node --check + 런타임 오류 + 스크립트 생성 요소 수
  python export.py shot  "덱.html" [--out DIR] [--block-cdnjs]   # 1·2장 스크린샷 (등장 애니메이션 완료 상태로 고정)
  python export.py pdf   "덱.html" [--out FILE]    # 인쇄 CSS 로 PDF (슬라이드 1장 = 1쪽)
  python export.py anims "덱.html"                 # 실행 중인 무한 반복 애니메이션과 주기(초) — 속도 판단용

주의
- GPU 를 끄지 않는다(--disable-gpu 는 3D 카드·캔버스를 비워 오판하게 만든다).
- 헤드리스에서는 애니메이션 시계가 진행되지 않으므로 스크린샷은 등장 애니메이션을 완료 상태로 고정한 사본으로 찍는다.
- Windows "애니메이션 효과 끄기" PC 에서는 prefers-reduced-motion 이 켜진다. 덱은 그 설정을 무시하도록 만들어져 있다.
"""
import os, sys, re, subprocess, tempfile, shutil, urllib.parse, html

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
]
CLAMP = ('<style>.rv,.h-reveal,.h-line,.holo::before,.stat .bar i,.prow .bar i{animation-duration:.001s!important;animation-delay:0s!important}'
         '.slide{transition-duration:.001s!important}.float>.ic,.blob,.bgcube .box,.core,.live i,.trace i{animation:none!important}</style>')
TRAP = '<script>window.__errs=[];addEventListener("error",e=>window.__errs.push(e.message+" @"+e.lineno+":"+e.colno));</script>'


def chrome():
    for p in CANDIDATES:
        if os.path.isfile(p):
            return p
    sys.exit("Chrome/Edge 실행 파일을 찾지 못했습니다. CANDIDATES 에 경로를 추가하세요.")


def file_url(p):
    p = os.path.realpath(p).replace("\\", "/")
    return "file:///" + urllib.parse.quote(p, safe="/:")


def run(args, timeout=120):
    subprocess.run([chrome(), "--headless=new", "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
                    "--user-data-dir=" + os.path.join(tempfile.gettempdir(), "axis-chrome-profile")] + args,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)


def dump(url, budget=10000, extra=()):
    r = subprocess.run([chrome(), "--headless=new", "--no-first-run", "--window-size=1600,900",
                        "--user-data-dir=" + os.path.join(tempfile.gettempdir(), "axis-chrome-profile"),
                        f"--virtual-time-budget={budget}", *extra, "--dump-dom", url],
                       capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


def with_injection(src, head_extra="", body_extra=""):
    s = open(src, encoding="utf-8").read()
    if head_extra:
        s = s.replace("</head>", head_extra + "</head>", 1)
    if body_extra:
        s = s.replace("</body>", body_extra + "</body>", 1)
    d = tempfile.mkdtemp(prefix="axis-")
    p = os.path.join(d, os.path.basename(src))
    open(p, "w", encoding="utf-8").write(s)
    return p


def cmd_check(src):
    s = open(src, encoding="utf-8").read()
    blocks = re.findall(r"<script(?: data-editor)?>(.*?)</script>", s, re.S)
    js = "\n;\n".join("(function(){" + b + "\n})();" for b in blocks)
    jp = os.path.join(tempfile.gettempdir(), "axis-check.js")
    open(jp, "w", encoding="utf-8").write(js)
    r = subprocess.run(["node", "--check", jp], capture_output=True, text=True)
    print("node --check:", "OK" if r.returncode == 0 else "FAIL\n" + r.stderr)
    probe = ('<script>setTimeout(()=>{const d=document.createElement("div");d.id="dbg";'
             'd.textContent="ERRS="+window.__errs.join(" | ")+" | PLIST_ROWS="+document.querySelectorAll("#plist .prow").length'
             '+" | CHART="+(typeof Chart)+" | EDITOR="+document.querySelectorAll("[data-editor]").length;document.body.appendChild(d);},2500);</script>')
    p = with_injection(src, TRAP, probe)
    out = dump(file_url(p) + "#s2")
    m = re.search(r'<div id="dbg">([^<]*)</div>', out)
    print("runtime:", html.unescape(m.group(1)) if m else "no result (페이지 로드 실패?)")


def cmd_shot(src, out_dir=None, block_cdnjs=False):
    out_dir = out_dir or os.path.dirname(os.path.realpath(src))
    p = with_injection(src, CLAMP)
    extra = ["--host-resolver-rules=MAP cdnjs.cloudflare.com 127.0.0.1"] if block_cdnjs else []
    base = os.path.splitext(os.path.basename(src))[0]
    for n in (1, 2):
        png = os.path.join(out_dir, f"{base}_s{n}.png")
        run(["--window-size=1600,900", "--virtual-time-budget=12000", *extra, f"--screenshot={png}", file_url(p) + f"#s{n}"])
        print("screenshot:", png)


def cmd_pdf(src, out=None):
    out = out or os.path.splitext(os.path.realpath(src))[0] + ".pdf"
    run(["--window-size=1600,900", "--virtual-time-budget=15000", "--no-pdf-header-footer", f"--print-to-pdf={out}", file_url(src)], timeout=180)
    print("pdf:", out)
    try:
        import pymupdf
        d = pymupdf.open(out)
        print(f"pages: {len(d)}  size: {d[0].rect.width:.0f}x{d[0].rect.height:.0f}pt")
    except ImportError:
        pass


def cmd_anims(src):
    probe = ('<script>setTimeout(()=>{const a=[...new Set(document.getAnimations().filter(x=>x.effect.getTiming().iterations===Infinity)'
             '.map(x=>x.animationName+"="+(x.effect.getTiming().duration/1000)+"s"))];const d=document.createElement("div");d.id="dbg";'
             'd.textContent="reduce="+matchMedia("(prefers-reduced-motion: reduce)").matches+" | slow="+getComputedStyle(document.documentElement).getPropertyValue("--slow")+" | "+a.join(", ");'
             'document.body.appendChild(d);},3000);</script>')
    p = with_injection(src, "", probe)
    out = dump(file_url(p), 5000)
    m = re.search(r'<div id="dbg">([^<]*)</div>', out)
    print(html.unescape(m.group(1)) if m else "no result")


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__); return
    cmd, src = a[0], a[1]
    opts = a[2:]
    out = opts[opts.index("--out") + 1] if "--out" in opts else None
    if cmd == "check": cmd_check(src)
    elif cmd == "shot": cmd_shot(src, out, "--block-cdnjs" in opts)
    elif cmd == "pdf": cmd_pdf(src, out)
    elif cmd == "anims": cmd_anims(src)
    else: print(__doc__)


if __name__ == "__main__":
    main()
