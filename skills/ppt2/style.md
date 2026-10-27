---
label: 홀로그램 (ppt2)
tagline: 글래스 카드 위에 발광 데이터 큐브 · 회로망 · 네온 시안 글로우
fit: 기술·데이터·AI 주제의 현황 보고 · 임팩트가 필요한 자리
---

# ppt2 스타일 규격 — 홀로그램 데이터 큐브

ppt1 의 토큰·격자·컴포넌트·차트·인쇄 규격을 그대로 쓴다(`../ppt1/style.md`). 여기에는 추가·변경분만 적는다.

## 1. 추가 토큰

| 토큰 | 값 | 쓰임 |
|---|---|---|
| `--neon` / `--neon-rgb` | `#2FD8FF` / `47,216,255` | 큐브 윤곽·글로우·스캔라인·링·펄스. 글자색으로는 쓰지 않는다 |
| `--violet` | `#6C5CE7` | 예비(현재 미사용) |

차트·텍스트 색은 ppt1 과 같다. 네온은 "빛"에만 쓴다.

## 2. 레이어 순서 (`.stage` 안)

`.grid`(점 격자, z0) → `.blob`×3(z0) → `#net`(회로망 캔버스, z1) → `.bgfx`(부유 큐브, z1) → `.deck`(z2) → `#glow`(z5) → `#ring`(z50)

## 3. 데이터 큐브 (`.cube-wrap`)

- 150×150, `perspective:900px`. 바깥 `.cube` 면 6개: 1.6px 시안 테두리, 안쪽 점선 테두리, 유리 그라데이션, `box-shadow 0 0 22px` 시안.
- 안쪽 `.cube.inner`(inset 40px): 파란 테두리, 반대 방향 회전.
- `.core`: 46px 흰→시안 방사형, blur 2px, `corepulse`.
- `.cube-shadow`: 바닥 타원 그림자.
- 2장용 `.s2-cube` 는 80×80 축소판.

## 4. 회로망 캔버스 (`#net`)

- 노드 수 `min(150, W*H/15000)`, 반지름 1.1~2.8px, 색 `rgba(31,91,224,.34)`.
- 128px 이내 노드끼리 선 연결(거리에 반비례한 투명도). 커서 230px 이내는 시안으로 밝아지고 노드가 커서 쪽으로 10% 끌린다.
- 데이터 펄스: 간선 위를 이동하는 흰 점 + 시안 후광(`shadowBlur 12`). 장 전환 시 `burst()` 로 6개 추가.
- 인쇄·PDF 에서는 숨긴다.

## 5. 홀로그램 등장

| 요소 | 키프레임 |
|---|---|
| `.rv` | `materialize 1s`: `translateY(28px) scale(.965) blur(10px) brightness(1.7)` → 중간 `brightness(1.18)` → 원상 |
| `.holo::before` | `scan 1.15s`: 시안+흰 가로 띠가 위→아래로 지나감(`background-position -80% → 190%`) |
| `.h-reveal` | `hreveal 1.5s`: `clip-path inset(0 100% 0 0)` → 열림, 시안 text-shadow 가 사라짐 |
| `.h-line` | 제목 끝을 따라가는 3px 시안 라인 |

## 6. 호버

- `.neon:hover`: `0 0 0 1px` 시안 링 + `0 0 30px` 시안 글로우 + 기본 그림자.
- `.neon::after`: 115° 흰/시안 띠가 좌→우로 한 번 스윕(`sweep 1s`).
- `.fterm:hover`, `.stat:hover`, `.insight li:hover`, `.prow:hover` 에도 1px 시안 링.
- `#ring`: 34px 시안 링이 커서를 따라오고(lerp .35) 카드·버튼 위에서 50px 로 커진다.

## 7. 디지털 카운터

`countUp`: 앞 20% 구간은 `fmt(Math.random()*end*1.3)` 난수 + `.glitch`(시안 text-shadow, 0.16s 깜빡임) → 이후 easeOutCubic 으로 수렴. 인쇄 시 `finishCounts()` 가 즉시 최종값.
