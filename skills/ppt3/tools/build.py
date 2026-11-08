#!/usr/bin/env python3
"""axis:ppt3 덱 조립 — template.html 의 견본 장을 걷어내고 내 슬라이드 조각을 끼운다.

  python build.py --slides week1-slides.html --out "덱.html" \
      [--template template.html] [--charts week1-charts.js] \
      [--title "덱 제목"] [--desc "한 줄 설명"] [--logo "AX:IS"] [--logo-sub "AI 기초 4주"] \
      [--menu "시작=1,역사=10,데이터=15,학습=18,정리=24"]

- --slides : <section class="slide">…</section> 들만 들어 있는 HTML 조각. 견본 장 대신 그대로 들어간다.
- --charts : `const charts={ … }` 의 중괄호 안쪽(키: 함수) 만 적은 JS. 없으면 차트 없음.
             canvas[data-chart="키"] 마다 같은 키의 함수가 있어야 한다. 조립 후 검사한다.
- --menu   : 상단 메뉴. "이름=장번호" 를 쉼표로. 없으면 템플릿 메뉴를 지우고 빈 메뉴로 둔다.
- --template 생략 시 이 파일 옆의 ../template.html.

조립 뒤 `export.py check` 와 `export.py shot` 으로 검증한다.
"""
import argparse, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))


def rd(p):
    return open(p, encoding="utf-8").read()


def must_sub(s, pat, rep, what, flags=0):
    s2, n = re.subn(pat, rep, s, count=1, flags=flags)
    if n == 0:
        sys.exit(f"템플릿에서 '{what}' 자리를 찾지 못했다: {pat[:60]}")
    return s2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default=os.path.join(HERE, "..", "template.html"))
    ap.add_argument("--charts")
    ap.add_argument("--title", default="")
    ap.add_argument("--desc", default="")
    ap.add_argument("--logo")
    ap.add_argument("--logo-sub")
    ap.add_argument("--menu", default="")
    a = ap.parse_args()

    s = rd(a.template)
    slides = rd(a.slides).strip("\n")
    n_slides = len(re.findall(r'<section class="slide', slides))
    if n_slides == 0:
        sys.exit("--slides 조각에 <section class=\"slide\"> 가 없다")

    # 메타
    if a.title:
        s = must_sub(s, r"<title>[^<]*</title>", "<title>" + a.title.replace("\\", "\\\\") + "</title>", "title")
    if a.desc:
        s = must_sub(s, r'<meta name="description" content="[^"]*">',
                     '<meta name="description" content="' + a.desc.replace('"', "&quot;").replace("\\", "\\\\") + '">', "description")
    if a.logo is not None:
        s = must_sub(s, r'(<div class="logo"><span class="mark"></span><b>)[^<]*(</b>)', r"\g<1>" + a.logo.replace("\\", "\\\\") + r"\g<2>", "logo")
    if a.logo_sub is not None:
        s = must_sub(s, r'(<div class="logo">.*?<small>)[^<]*(</small>)', r"\g<1>" + a.logo_sub.replace("\\", "\\\\") + r"\g<2>", "logo-sub")

    # 메뉴
    btns = ""
    if a.menu:
        for item in a.menu.split(","):
            name, _, num = item.partition("=")
            name, num = name.strip(), num.strip()
            if not name or not num.isdigit():
                sys.exit(f"--menu 항목이 이상하다: {item!r} (이름=장번호)")
            if int(num) > n_slides:
                sys.exit(f"--menu {name}={num} 가 장 수({n_slides})를 넘는다")
            btns += f'<button data-go="{num}">{name}</button>'
    s = must_sub(s, r'(<div class="menu" id="menu">\n?)(?:\s*<button[^<]*</button>)*(\s*</div>)', r"\g<1>      " + btns.replace("\\", "\\\\") + r"\n    \g<2>", "menu", re.S)
    s = must_sub(s, r'<span id="tot">\d+</span>', f'<span id="tot">{n_slides:02d}</span>', "tot")

    # 견본 장 → 내 장
    start = s.find("  <!-- ═══════ 견본")
    end = s.find('\n  <div class="bottombar">')
    if start < 0 or end < 0 or end < start:
        sys.exit("템플릿의 견본 장 구간(견본 주석 … bottombar)을 찾지 못했다")
    s = s[:start] + slides + "\n" + s[end:]

    # 차트
    body = rd(a.charts).strip() if a.charts else ""
    m = re.search(r"const charts=\{.*?\n\};\n", s, re.S)
    if not m:
        sys.exit("템플릿의 const charts={…}; 블록을 찾지 못했다")
    s = s[:m.start()] + "const charts={\n" + body + ("\n" if body else "") + "};\n" + s[m.end():]

    # 검사: canvas 키 ↔ charts 키
    keys_used = set(re.findall(r'data-chart="([^"]+)"', slides))
    keys_def = set(re.findall(r"^\s*([A-Za-z_$][\w$]*)\s*\(c\)\s*\{", body, re.M))
    missing = keys_used - keys_def
    if missing:
        sys.exit(f"charts 에 정의가 없는 data-chart 키: {sorted(missing)}")
    unused = keys_def - keys_used
    if unused:
        print("경고: 쓰이지 않는 charts 키:", sorted(unused))

    # 검사: 도식 화살표 끝 박스
    for frm, to in re.findall(r'data-from="([^"]+)" data-to="([^"]+)"', slides):
        for i in (frm, to):
            if f'id="{i}"' not in slides:
                sys.exit(f"도식 화살표의 끝 박스 id={i} 가 없다")
    dg_ids = re.findall(r'<div class="dg-node[^"]*" id="([^"]+)"', slides)
    dup = {i for i in dg_ids if dg_ids.count(i) > 1}
    if dup:
        sys.exit(f"도식 박스 id 가 겹친다(덱 전체에서 유일해야 한다): {sorted(dup)}")

    open(a.out, "w", encoding="utf-8").write(s)
    editor = len(re.findall(r"<(style|span|script)[^>]* data-editor(?:=\"\")?>", s))
    print(f"wrote {a.out}  {len(s):,} bytes | slides {n_slides} | charts {len(keys_def)} | dg {s.count('class=\"dg\"')} | data-editor {editor} (4 이어야 함)")


if __name__ == "__main__":
    main()
