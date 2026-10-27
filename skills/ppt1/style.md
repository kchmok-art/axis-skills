---
label: 글래스 (ppt1)
tagline: 연블루 유리 카드 · 광택 3D 아이콘 · 블루 포인트 한 가지
fit: 성과 지표·현황 보고 · 숫자가 주인공인 2장짜리 발표
---

# ppt1 스타일 규격 — 글래스

디자인 레퍼런스: 연블루 글래스모피즘 PPT 템플릿(흰 유리 카드, 둥근 필 라벨, 광택 3D 아이콘, 파란 포인트).

## 1. 토큰 (`:root`)

| 토큰 | 값 | 쓰임 |
|---|---|---|
| `--bg` / `--bg-2` | `#E8EFF9` / `#F7FAFE` | 바탕 그라데이션 |
| `--ink` / `--ink-2` / `--ink-3` | `#16243A` / `#4A5A72` / `#7F8DA5` | 제목 / 본문 / 보조 |
| `--accent` / `--accent-deep` / `--accent-2` | `#1F5BE0` / `#1240B8` / `#7FB5F5` | 포인트 / 진한 포인트 / 연한 포인트(차트 2번 시리즈) |
| `--accent-soft` / `--accent-tint` | `#DCE9FB` / `#EEF4FD` | 테두리 / 내부 타일 바탕 |
| `--target` | `#E0582B` | 목표선·격차(경고색, 시리즈 색으로 쓰지 않음) |
| `--gap` | `#D9E1EC` | 게이지의 "남은 격차" |
| `--glass` / `--glass-strong` | `rgba(255,255,255,.72)` / `.92` | 카드 유리 |
| `--shadow` | `0 18px 50px rgba(31,91,224,.13)` | 카드 그림자 |
| `--font` | `'NanumSquare', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif` | 나눔스퀘어 L/R/B/EB (jsdelivr `moonspam/NanumSquare`) |
| `--slow` | `0.4` | 상시 모션 배속(클수록 느림). 확정값 |

차트 팔레트는 `#1F5BE0`(핵심) · `#7FB5F5`(전공) 두 가지. dataviz 검증기 통과(CVD ΔE 24.9). 연한 색은 대비 3:1 미만이라 **막대 끝 값 라벨을 항상 그린다**.

## 2. 격자

- 슬라이드 1600×900 고정, 뷰포트에 `scale(min(vw/1600, vh/900))`. 패딩 `44px 64px 50px`.
- 상단 바 46px: 좌 로고 마크 + 브랜드 글자(`.brand-t`) + 작은 부제, 우 기준일 + `01 / 02`.
- 1장 본문 `grid-template-columns: 640px 1fr; gap: 36px`. 우측은 `auto 1fr auto`(KPI / 게이지 / 칩).
- 2장 본문 `grid-template-columns: 1fr 560px; gap: 22px`. 우측 `auto 1fr`(핵심 포인트 / 우선 관리).
- 각주 26px: 첫 span `max-width:36%`, `.foot-cap` 은 `width:calc(100% - 676px)` 로 우측 열 시작선(x=740)에 맞춘다.
- 하단 내비 필은 `bottom:12px`, 높이 38px — 각주(바닥에서 50px 위)와 겹치지 않는다.

## 3. 컴포넌트

| 클래스 | 규격 |
|---|---|
| `.card` | 유리 배경 + 1px 흰 테두리 + 22px 라운드 + `backdrop-filter: blur(18px)` |
| `.pill` | 높이 30px, 파란 그라데이션, 흰 글자 12.5px/700. `.ghost` 는 흰 바탕 파란 글자 |
| `.kpi` | 92px 높이, 라벨 12px → 값 26px/800 파란색 + 단위 13px → 보조 11px. 우상단 아이콘 34px |
| `.formula .fterm` | 148px 폭 타일, 아이콘 56px, 라벨 12px, 값 22px |
| `.fresult` | 파란 결과 밴드: `=` 30px · 값 42px · 라벨 14.5px + 산식 11.5px · 우측 목표 필 |
| `.gauge-card` | `1fr 250px`; 반원 도넛(cutout 68%, rotation −90, circumference 180) 중앙에 50px 숫자 |
| `.stat` | 라벨 12px + 값 26px + 6px 진행 막대(`--w`) |
| `.chip` | 숫자 24px(상태색: 달성 `#1B8A5A`, 경고 `--target`, 무관 `--ink-3`) + 제목 12px + 보조 10.5px |
| `.insight li` | `34px 1fr` 격자, 아이콘 34px, 제목 14px/800, 본문 12.5px, 호버 시 흰 배경·우측 5px 이동 |
| `.prow` | `150px 58px 1fr 54px`, 12.5px, 막대 9px(점선 = 평균 위치), 지수 14px/800 파랑 |
| `.side h2::before` | 4px 세로 강조선(연→진 파랑 그라데이션) |

## 4. 아이콘 (직접 그린 SVG `<symbol>`)

`#tile`(96×96 라운드 22, 그라데이션 `#8BBCF7→#1F5BE0`, 상단 광택) 위에 흰 도형.
`ic-badge`(핵심역량) · `ic-cap`(전공역량) · `ic-people`(재학생) · `ic-target`(목표, 주황) · `ic-star`(비교과) ·
`ic-chart` · `ic-up`(민트, 상승) · `ic-alert`(주황, 경고) · `ic-cube`(로고) · `ic-doc`(유리 문서) · `ic-stairs`(계단 성장).
글자는 SVG 안에 넣지 않는다(편집 대상이 되도록 HTML 로).

## 5. 효과 (스토리텔링 원페이지 참고)

| 효과 | 구현 |
|---|---|
| 스태거 등장 | `.rv{--i}` → `rise .9s` + `--i×95ms` 지연. 장이 활성화될 때마다 재생 |
| 마우스 패럴랙스 | 포인터 위치를 `--px/--py` 로 두고 블롭·부유 아이콘이 `--d` 깊이만큼 이동. lerp `.035/SLOW` |
| 글래스 틸트 | `.tilt` 카드가 ±7°/9° 기울고 `::after` 광택이 커서를 따라감. 편집 중엔 끔 |
| 커서 글로우 | 620px 방사형 빛 `mix-blend-mode: soft-light` |
| 카운트업 | `[data-count]` 1.5s easeOutCubic. 인쇄 시 즉시 최종값 |
| 슬라이드 전환 | 블러 14px + 46px 이동 .75s |
| 상시 모션 | 블롭 드리프트 `calc(52s*var(--slow))`, 아이콘 부유 `calc(var(--t,9s)*var(--slow))` |

## 6. 차트 (Chart.js 4.5)

- 게이지: doughnut, 데이터 `[핵심, 전공, 목표−현재]`, 색 `[accent, accent-2, gap]`, `spacing:3`, `borderRadius:7`, 중앙 글자는 HTML 오버레이.
- 막대: bar + `indexAxis:'y'`, 두 시리즈 stacked, `maxBarThickness:15`, 2번 시리즈 `borderWidth:{left:2}` 흰색으로 분리.
  플러그인 3개: `band`(평균 이하 영역), `refLines`(평균·목표 점선 + 상단 라벨), `endLabels`(막대 끝 지수). 우선 관리 대상은 y 라벨 굵게.
- 툴팁: 어두운 배경, 제목 = 정식 명칭, 본문 = 시리즈 % (인원), 푸터 = 지수·평균 대비·재학생·비교과.
- 로드: cdnjs → 실패 시 jsdelivr(`ensureChart`) → 둘 다 실패 시 `.chart-fallback` 문구.

## 7. 인쇄

`@page 1600px 900px`, 슬라이드마다 `break-after:page`, 내비·편집 도구·블롭 숨김, `.rv` 애니메이션 없음, 카드 배경 `.9`, `print-color-adjust:exact`.
`beforeprint` 에서 `finishCounts()` 가 숫자·차트를 최종 상태로 고정한다.
