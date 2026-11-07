---
label: 라이트 그라디언트 카드 (ppt3)
tagline: 연한 바탕 · 흰 둥근 카드 · 블루→바이올렛→핑크 강조 · 글로잉 큐브 배경
fit: 강의 · 동아리 발표 · 개념 설명처럼 장이 많은 덱
---

# ppt3 스타일 규격

## 1. 토큰 (`:root`)

| 토큰 | 값 | 쓰임 |
|---|---|---|
| `--bg` / `--bg2` | `#f5f7fc` / `#eef2fb` | 바탕 |
| `--ink` / `--ink-2` / `--muted` / `--faint` | `#0f1a2e` / `#2b3850` / `#5f6b80` / `#9aa5b8` | 제목 / 본문 / 보조 / 각주 |
| `--blue` `--violet` `--pink` `--cyan` `--green` `--red` `--amber` | `#3b82f6 #8b5cf6 #ec4899 #22d3ee #10b981 #ef4444 #f59e0b` | 강조색. 글자에는 blue·violet 만 |
| `--grad` | `135deg #3b82f6 → #8b5cf6 55% → #ec4899` | 제목 강조(`.g`), 밴드 점, 단계 번호, 로고 |
| `--grad-soft` | `#dbe7ff → #e9ddff → #ffdfeb` | 아이콘 배경 |
| `--shadow` / `--shadow-hover` | 연한 블루 그림자 | 카드·칩·밴드 |
| `--r` | `22px` | 카드 모서리 |

폰트: `PretendardVariable`(45~930) → `Pretendard` → 시스템. 본문 굵기 450, 굵게 750. `word-break:keep-all`.

## 2. 스테이지와 격자

- `.stage` 1600×900 고정, 화면에 맞춰 `--s` 배율 × `--zoom`(사용자 `[` `]`).
- `.topbar` 76px(로고 · 메뉴 · 카운터), `.bottombar` 하단 28px 위(진행 바 · 편집 도구 · 힌트 · ←→).
- `.slide` 패딩 `112px 80px 90px`, 세로 flex, 간격 18px. **본문 블록은 y 840px 안에서 끝나야 한다**(`export.py overflow` 기준).
- `.body` 는 `flex:1` 그리드. 열 구성: `two`(1:1) · `two w`(1.15:0.85) · `three` · `four`.

## 3. 장 유형과 권장 구성

| 유형 | 클래스 | 구성 | 글자 한도(권장) |
|---|---|---|---|
| 타이틀 | `slide s-title` | 좌: `.pill` → `h1.title`(2줄, 84px) → `.lead` → `.band.dark` / 우: `.scene`(큐브·링·회로 + `.chip` 4개) | lead 2줄, 칩 라벨 12자 |
| 두 칸 카드 | `slide` + `.body.two` | `.card.hot/.dim` ×2 (`h3 > small + span`, `p`, 선택: `.ill` 200px) | 카드 p 3줄 |
| 단계 + 그림 | `.body.two.w` | 좌 `.steps > .step`(번호 `.n` + `b` + `span`) 3~4개 / 우 `.ill`(SVG) 또는 `.chart` | step b 18자, span 32자 |
| 세 칸 | `.body.three` | `.card` ×3 (태그 `.tag`, `.big`, `p` 또는 `ul.list`) | li 5개 |
| 네 칸 | `.body.four` | `.card` ×4 (이모지 40px + `h3` + `p`) | p 3줄 |
| 플로우 | `.body` > `.flow` | `.card` → `.arrow` → `.card` → `.arrow` → `.card`(`.ill` 120px + `h3` + `p` + `p.src`) | 카드 3개 고정 |
| 통계 타일 | `.body.two.w` | 좌 `.three` 그리드에 `.card > .stat`(`.v` 큰 숫자 · `.l` · `.s`) ×3 / 우 `.chart` | v 4자 |
| 질문 | `slide s-ask` | 가운데 `h1`(64px, 2줄) + `.body.ill`(SVG 800×300) + `.band.dark` | — |
| 도식 | `.body` > `.dg[data-size="1440x400"]` | `.dg-node`(`b`+`span`, 변형 `.ink` `.lime` `.zone` `.ghost`) + `.dg-edge[data-from][data-to][data-label][data-style=dashed][data-tone=muted][data-curve][data-arrow=both]` | 박스 ≤ 7 |

공통: 맨 위 `.kicker`(소제목), `h1.title`(54px, 핵심구 `<span class="g">`), 선택 `.lead`(20px, 1줄), 맨 아래 `.band`(한 줄 결론; `.band.dark` 는 강한 결론).

## 4. 컴포넌트 세부

- **카드** `.card`: 흰 배경, 1px 선, 그림자, 호버 시 그라디언트 테두리 + 글로우 + 3D 틸트. `.hot`(보라빛) `.dim`(회색빛) `.ink`(짙은 남색, 글자 흰색).
- **태그** `.tag`(+ `.red .green .violet .amber`), **리스트** `ul.list`(그라디언트 점) `.x`(붉은 점) `.ok`(초록 점).
- **단계** `.step`(`.ok` 초록 번호, `.off` 회색 번호). 호버 시 오른쪽 8px 이동.
- **통계** `.stat .v` 56px 그라디언트 숫자.
- **차트** `.chart`: `h4 > span + small`, `.cv > canvas[data-chart]`. Chart.js 4.4.1(cdnjs). 공용: `gradV/gradH`, `endLabels`(막대 끝 값), `centerText`(도넛 중앙 글자), `DPR`.
- **일러스트** `.ill svg`: `class="lbl"`(15px 굵게) `class="sub"`(12.5px 보조) `class="draw"`(선 그리기 애니메이션) `class="pulse"` `class="floaty"`.
- **칩** `.chip`(타이틀 장): `em` 큰 숫자 + `b` 라벨 + `small` 출처. `data-d` 로 마우스 반응 깊이.
- **프롬프트 상자** `.prompt`(`.dark`), **키캡** `.kbd`, **앱 목업** `.mock`.

## 5. 효과 (손대지 않는다)

배경: 블롭 3개(커서 반대로 이동) · 파티클 네트워크 캔버스(커서 근처 시안 연결) · 떠다니는 와이어 큐브 5개 · 스포트라이트.
타이틀: 홀로그램 큐브(`#hcube`, 커서 기울기) · 점선 링 2개 · 회로 선.
등장: `.r` + `--i` → `holo`(블러·밝기 → 선명) 0.8s, 0.11s 스태거. 전환은 opacity 0.35s.
`prefers-reduced-motion` 에서는 등장만 생략하고 효과는 유지한다.

## 6. 편집·도식·인쇄

- 편집 대상 선택자(`SEL`)는 제목·본문·카드·단계·리스트·통계·칩·SVG `text`·로고까지 덮는다. 새 글자는 이 선택자 안에 둔다(`p`, `b`, `span`, `small`, `li`, `h3`, `svg text`).
- 도식은 편집을 켜면 박스 드래그·크기 조절·연결·복제·모양·휘기·삭제가 되고, 저장 시 `.dg-node` 좌표와 `.dg-edge` 데이터만 남는다.
- 인쇄: `@page 1600×900`, `.slide` 가 relative 로 쌓여 1장 = 1쪽. 배경·내비·도구 숨김. `beforeprint` 가 차트를 최종값으로 만들고 도식을 그린다.

## 7. 퀴즈 장 (`.quiz`)

강의 덱에 원 코스의 퀴즈를 그대로 싣는 장. `.body > .quiz`(2열 격자) 안에 문항 카드 `.q` 를 6개까지(3행) 둔다.

```html
<div class="q"><span class="qt">M1 · Q3</span><b><i>03</i>질문(한국어)</b>
  <ol><li data-k="A">option</li><li data-k="B" class="ok">correct option</li>…</ol>
  <small>해설 한 줄</small></div>
```
- 보기는 원문 언어 그대로(영어), 질문·해설은 한국어. 보기가 길면 `ol.one`(1열).
- 복수 정답은 `li.ok` 를 여러 개. 빈칸 채우기는 정답 문자열을 `li.ok` 하나로.
- 문항 글자 14.5px · 보기 12.5px · 해설 11.5px 고정. 한 장에 7개 이상 넣지 않는다(넘침 검사로 확인).
