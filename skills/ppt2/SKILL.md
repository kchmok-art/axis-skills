---
name: ppt2
description: 홀로그램 데이터 큐브 스타일의 16:9 HTML 현황 보고 슬라이드를 만든다. ppt1 과 같은 2장 구성(KPI·산식·Chart.js 게이지와 누적 막대·핵심 포인트·우선 관리 목록)에 발광 3D 데이터 큐브, 회로망 파티클 캔버스, 홀로그램 스캔 리빌, 네온 엣지, 디지털 카운터 같은 테크 모션을 입힌다. 글자 편집(E·Ctrl+S)·PDF·느린 모션 포함. "홀로그램 스타일 / 테크 느낌 발표 / 데이터 큐브 덱 / axis ppt2" 같은 요청에 사용한다.
---

# axis:ppt2 — 홀로그램 데이터 큐브 덱

`axis:ppt1` 과 **내용·레이아웃·데이터 블록·편집 엔진·검증 절차가 같고, 효과 레이어만 다르다.**
그래서 이 문서는 차이만 적는다. 데이터 읽기 → 2장 구성 → 만들기 → 검증 → PDF → 전달 절차와 확정 규칙은
`${CLAUDE_PLUGIN_ROOT}/skills/ppt1/SKILL.md` 를 그대로 따른다. 템플릿은 이 폴더의 `template.html` 을 쓴다.

효과 레퍼런스: Envato "Interactive Data Cube Reveal"(발광 큐브, 회로망, 홀로그램 리빌)을 웹 효과로 재해석한 것.
디자인(연블루 글래스 카드)은 ppt1 과 동일하고, 네온 시안 `--neon:#2FD8FF` 한 가지가 글로우 색으로 추가된다.

---

## 1. ppt1 과 다른 점

| 항목 | ppt1 (글래스) | ppt2 (홀로그램) |
|---|---|---|
| 배경 | 블롭 3개 | 블롭 + 점 격자 + **회로망 파티클 캔버스**(`#net`) + 부유 와이어 큐브 5개(`#bgfx`) |
| 히어로 장식 | 광택 배지 아이콘 | **발광 데이터 큐브**(바깥 큐브 + 안쪽 큐브 + 코어 글로우, CSS 3D, 커서를 따라 기움) |
| 등장 | `rise` 스태거 | `materialize`(블러·밝기) + 카드 **스캔라인**(`.holo::before`) + 제목 **홀로그램 리빌**(`.h-reveal`, 시안 라인) |
| 카드 호버 | 틸트 + 광택 | 틸트 + **네온 엣지 글로우** + **라이트 스윕**(`.neon::after`) |
| 커서 | 글로우 | 글로우 + **시안 링**(`#ring`, 카드 위에서 커짐) |
| 전환 | 블러 슬라이드 | **3D 회전**(`rotateY 18deg` + 블러) |
| 카운트업 | 숫자 증가 | **디지털 스크램블**(앞 20% 구간 난수 깜빡임 `.glitch`) 후 증가 |
| KPI 아래 | 없음 | **데이터 펄스 트레이스**(`.trace`, 빛 점 2개) |
| 상단 바 | 기준일 | `DATA ·` 표시등(`.live i` 깜빡임) |
| 2장 장식 | 계단 아이콘 | 작은 데이터 큐브(`.s2-cube`, 제목 줄 우측에 absolute) |

템플릿의 효과 CSS/JS 는 손대지 않는다. 글자·데이터만 바꾼다(ppt1 3절과 같음).

## 2. 상시 모션 (모두 `--slow` 배속, 확정값 0.4)

| 모션 | 주기 (`--slow:0.4` 기준) | 구현 |
|---|---|---|
| 데이터 큐브 회전 | 약 48초/바퀴 | JS `ang += .05/SLOW`, `rotateY(ang + pos.x*10)` |
| 배경 큐브 회전 | 44~68초 | `spin3d calc(var(--t)*var(--slow))`, `--t` 는 JS spec(110~170s) |
| 코어 맥동 | 2.2초 | `corepulse calc(5.5s*var(--slow))` |
| 트레이스 빛 점 | 4.4~5.6초 | `pulse-run calc(var(--t)*var(--slow))` |
| DATA 표시등 | 1.3초 | `blink calc(3.2s*var(--slow))` |
| 회로망 점 표류 | ±0.07/SLOW px/frame | `nresize()` 에서 속도 부여 |
| 데이터 펄스 | 최대 4개, 생성 확률 `.02/SLOW` | `ndraw()` |
| 블롭·부유 아이콘 | ppt1 과 동일 | |

## 3. ppt2 에서만 주의할 것

- **헤드리스 `--disable-gpu` 로 찍으면 2장이 비어 보인다**(3D 변환 카드·캔버스 미표시). `tools/export.py` 는 GPU 를 켠다. 소프트웨어 렌더 결과로 레이아웃을 판단하지 않는다.
- 큐브 면 배치는 JS 가 `translateZ` 를 넣는다. 히어로 큐브 150px(면 75/35), 2장 큐브 80px(면 30/11). 크기를 바꾸면 JS 의 두 숫자도 맞춘다.
- `.s2-cube` 는 제목 줄에 absolute(`right:0; bottom:-4px`)라 상단 바와 겹치지 않도록 80px 를 넘기지 않는다.
- 편집 저장 시 `html()` 이 `#bgfx` 자식과 `.cube`·`.cube .f` 의 inline transform 을 걷어낸다. 효과 요소를 추가하면 이 목록에도 추가한다.
- 회로망 캔버스는 `pointer-events:none` 이고 커서 근처에서만 시안으로 밝아진다. 성능 문제가 있으면 노드 수(`W*H/15000`, 최대 150)를 줄인다.

## 4. 검증·PDF·전달

ppt1 과 같다. 명령만 이 폴더 기준:

```bash
python "${CLAUDE_SKILL_DIR}/tools/export.py" check "덱.html"
python "${CLAUDE_SKILL_DIR}/tools/export.py" shot  "덱.html"
python "${CLAUDE_SKILL_DIR}/tools/export.py" pdf   "덱.html"
python "${CLAUDE_SKILL_DIR}/tools/serve.py" --open "덱.html"
```

PDF 에서는 캔버스·큐브·회로망이 빠지고(인쇄 CSS) 카드와 차트만 남는다. 1장 히어로 큐브는 CSS 3D 라 PDF 에 그대로 찍힌다.
