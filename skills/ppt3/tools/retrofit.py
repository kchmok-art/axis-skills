#!/usr/bin/env python3
"""axis:ppt3 편집 엔진 이식 — 편집 기능이 없는 기존 덱에 template.html 의 편집 엔진을 끼워 넣는다.

  python retrofit.py "기존덱.html" --out "기존덱_v2.html" [--template ../template.html]

편집 엔진이 들어오기 전에 만든 덱, 또는 손으로 고치다 엔진이 빠진 덱에 쓴다.
장(section)·CSS·차트·덱 고유 스크립트는 그대로 두고, 아래만 템플릿에서 가져와 붙인다.

  붙이는 것                                   data-editor   발표용(편집 기능 삭제) 뒤
  편집 CSS · 하단 [편집] 도구 · 편집 스크립트 2개   있음          빠진다
  화면 배율 · 도식 보기 · 도식 CSS · 인쇄 CSS · 인쇄 준비  없음          남는다

덱 제어 스크립트에는 편집기가 기대는 고리만 고친다 (각각 정확히 한 군데를 찾아야 하며, 못 찾으면 멈춘다):
  - go() 끝에 'deck:slide' 이벤트 (마지막 장 [편집 기능 삭제] · 도식 다시 그리기가 듣는다)
  - 장 넘기기 keydown: 글자를 고치는 중이면 무시
  - 빈 곳 클릭 · 스와이프: 편집 중이면 장을 넘기지 않음
  - .stage 의 scale 에 --zoom 곱하기 · 하단 힌트에 E 편집 · [ ] 배율

이미 편집 엔진이 있는 덱(id="edit")이면 아무것도 하지 않는다.
"""
import argparse, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))


def rd(p):
    return open(p, encoding="utf-8").read()


def grab(src, pat, what, n=1):
    found = re.findall(pat, src, re.S)
    if len(found) != n:
        sys.exit(f"템플릿에서 '{what}' 덩이를 {n}개 찾아야 하는데 {len(found)}개다 — 템플릿이 바뀌었으면 retrofit.py 의 패턴을 맞출 것")
    return found if n > 1 else found[0]


def patch_once(s, pat, rep, what, flags=re.S):
    s2, k = re.subn(pat, rep, s, count=1, flags=flags)
    if k != 1:
        sys.exit(f"덱에서 '{what}' 자리를 찾지 못했다 — 이 덱은 ppt3 계열 구조가 아니거나 손으로 많이 바뀌었다. 직접 확인할 것")
    return s2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default=os.path.join(HERE, "..", "template.html"))
    a = ap.parse_args()

    s, t = rd(a.deck), rd(a.template)
    if 'id="edit"' in s:
        sys.exit("이미 편집 엔진(id=\"edit\")이 있는 덱이다 — 이식하지 않는다")
    for need, what in (("function go(", "go()"), ('class="bottombar"', ".bottombar"), ('class="stage"', ".stage"),
                       ("const slides=", "slides"), ('class="nav"', ".nav")):
        if need not in s:
            sys.exit(f"ppt3 계열 덱이 아니다 — {what} 가 없다")

    # ── 템플릿에서 덩이 꺼내기 ──
    css_dg = grab(t, r"<style>\n/\* ───────── 도식\(\.dg\) 보기.*?</style>\n", "도식 보기 CSS")
    css_ed = grab(t, r"<style data-editor>.*?</style>\n", "편집 CSS")
    css_pr = grab(t, r"<style>\n/\* ───────── 인쇄·PDF.*?</style>\n", "인쇄 CSS")
    tools = grab(t, r'    <span class="tools" data-editor>.*?<i class="tools-sep"></i>\n    </span>\n', "하단 편집 도구")
    js_zoom = grab(t, r"<script>\n/\* ───────── 화면 배율.*?</script>\n", "배율 스크립트")
    js_dgv = grab(t, r"<script>\n/\* ───────── 도식 보기.*?</script>\n", "도식 보기 스크립트")
    js_print = grab(t, r"<script>\n/\* ───────── 인쇄 준비.*?</script>\n", "인쇄 준비 스크립트")
    js_ed = grab(t, r"<script data-editor>.*?</script>\n", "편집 스크립트", n=2)

    # ── CSS: </head> 앞 ──
    head = ""
    if ".dg-fit{" not in s:
        head += css_dg
    head += css_ed
    if "@page{size:1600px 900px" not in s:
        head += css_pr
    else:
        print("참고: 덱에 이미 인쇄 CSS 가 있어 템플릿 인쇄 CSS 는 넣지 않았다")
    s = patch_once(s, r"</head>", lambda m: head + "</head>", "</head>")

    # ── 하단 도구: 힌트 앞 ──
    s = patch_once(s, r'(\n)(\s*<span class="hint">)', lambda m: m.group(1) + tools + m.group(2).lstrip("\n"), "하단 힌트(.hint)")
    if "편집" not in re.search(r'<span class="hint">.*?</span>\s*<div class="nav">', s, re.S).group(0):
        s = patch_once(s, r'(<span class="hint">.*?)(</span>\s*<div class="nav">)',
                       lambda m: m.group(1) + ' · <span class="kbd">E</span> 편집 · <span class="kbd">[</span><span class="kbd">]</span> 배율' + m.group(2),
                       "힌트 문구")

    # ── 덱 제어 스크립트의 고리 ──
    if "deck:slide" not in s:
        s = patch_once(s, r"(location\.hash='#'\+\(cur\+1\);)",
                       lambda m: m.group(1) + "\n  document.dispatchEvent(new CustomEvent('deck:slide',{detail:{i:cur,last:cur===total-1}}));",
                       "go() 의 location.hash")
    guard = "  if(e.target.isContentEditable||(e.target.closest&&e.target.closest('input,textarea')))return;\n"
    s = patch_once(s, r"(addEventListener\('keydown',e=>\{\n)(?=(?:(?!addEventListener).){0,600}ArrowRight)",
                   lambda m: m.group(1) + guard, "장 넘기기 keydown")
    s = patch_once(s, r"(getElementById\('stage'\)\.addEventListener\('click',e=>\{\n)",
                   lambda m: m.group(1) + "  if(document.body.classList.contains('editing')||(e.target.closest&&e.target.closest('[contenteditable],.dg')))return;\n",
                   "빈 곳 클릭")
    if re.search(r"addEventListener\('touchend',e=>\{", s):
        s = patch_once(s, r"(addEventListener\('touchend',e=>\{)",
                       lambda m: m.group(1) + "if(document.body.classList.contains('editing'))return;", "스와이프")
    if "--zoom" not in s:
        s = patch_once(s, r"(\.stage\{[^}]*?)scale\(var\(--s,1\)\)", lambda m: m.group(1) + "scale(calc(var(--s,1)*var(--zoom,1)))", ".stage scale")

    # ── 스크립트: </body> 앞 (덱 제어 스크립트 뒤라야 go·cur·slides·made·charts 를 본다) ──
    tail = js_zoom + "\n" + js_dgv + "\n"
    if "beforeprint" not in s:
        tail += js_print + "\n"
    tail += js_ed[0] + "\n" + js_ed[1]
    s = patch_once(s, r"</body>(?![\s\S]*</body>)", lambda m: tail + "</body>", "</body>")

    open(a.out, "w", encoding="utf-8").write(s)
    editor = len(re.findall(r"<(style|span|script)[^>]* data-editor(?:=\"\")?>", s))
    print(f"wrote {a.out}  {len(s):,} bytes | slides {s.count('<section class=\"slide')} | data-editor {editor} (4 이어야 함)"
          f" | id=edit {s.count('id=\"edit\"')} | id=final {s.count('id=\"final\"')}")
    print("다음: export.py check → shot 으로 확인. 스크립트가 실행 중에 만드는 요소에는 data-runtime 을 붙여 저장에서 빠지게 할 것")


if __name__ == "__main__":
    main()
