# axis — Claude Code 스킬 라이브러리

`axis:something` 형태로 쓰는 개인 스킬 모음입니다. 지금은 발표 덱 스킬 두 개가 들어 있습니다.

| 스킬 | 호출 | 한 줄 |
|---|---|---|
| **ppt1** | `/axis:ppt1` | 연블루 글래스 스타일 · 16:9 HTML 현황 보고 덱 2장 (KPI · 산식 그림 · Chart.js 게이지/누적 막대 · 핵심 포인트 · 우선 관리 목록) |
| **ppt2** | `/axis:ppt2` | 같은 구성에 홀로그램 데이터 큐브 · 회로망 파티클 · 스캔 리빌 · 네온 글로우 효과 |

두 스킬 모두 결과 HTML 에 **글자 직접 편집(E · Ctrl+S 저장)**, **발표용 내보내기**, **PDF 인쇄 CSS**, **느린 자연스러운 모션(`--slow`)**, **마우스 반응 효과**가 들어 있습니다.

## 설치

Claude Code 안에서:

```
/plugin marketplace add kchmok-art/axis-skills
/plugin install axis@axis
```

터미널에서(비대화형):

```bash
claude plugin marketplace add kchmok-art/axis-skills
claude plugin install axis@axis
```

설치 후 `/axis:ppt1`, `/axis:ppt2` 로 부르거나 "이 데이터로 현황 보고 슬라이드 만들어줘" 라고 말하면 됩니다.

갱신: `/plugin marketplace update axis` 뒤 Marketplaces 탭에서 Update.

## 구조

```
axis/
├── .claude-plugin/
│   ├── marketplace.json   ← 이 저장소가 곧 마켓플레이스 (name: axis)
│   └── plugin.json        ← 플러그인 axis
├── skills/
│   ├── ppt1/  SKILL.md · style.md · template.html · tools/{export.py, serve.py, README.md}
│   └── ppt2/  SKILL.md · style.md · template.html · tools/{export.py, serve.py, README.md}
└── README.md · LICENSE
```

### 새 스킬 추가하기

`skills/{이름}/SKILL.md` 를 추가하면 `/axis:{이름}` 으로 바로 쓸 수 있습니다.

- `SKILL.md` frontmatter 의 `name` 은 폴더명과 같게, `description` 에는 "언제 쓰는지"를 한국어 트리거 문구까지 넣습니다.
- 스킬이 쓰는 파일은 같은 폴더에 두고 `${CLAUDE_SKILL_DIR}/...` 로 가리킵니다. 다른 스킬의 파일은 `${CLAUDE_PLUGIN_ROOT}/skills/...` 로 가리킵니다.
- 사용자 피드백으로 확정된 규칙은 SKILL.md 의 "확정된 규칙" 절에 번호를 매겨 쌓습니다.
- 올리기 전에 `claude plugin validate .` 로 검사합니다.

## 템플릿 데이터

`template.html` 의 학과명·수치는 **예시 데이터**(A학과~X학부)입니다. 스킬이 실제 데이터로 바꿔 씁니다.

## 크레딧·라이선스

- 이 저장소: MIT (LICENSE)
- 인라인 편집·저장 서버 엔진: [RDDcat/maro-ppt](https://github.com/RDDcat/maro-ppt) (MIT) 의 편집 기능을 이 덱 구조에 맞게 옮겨 넣은 것
- 차트: [Chart.js](https://www.chartjs.org/) (MIT, cdnjs/jsdelivr 로 로드)
- 글꼴: 나눔스퀘어 (네이버, OFL 유사 무료 라이선스, jsdelivr `moonspam/NanumSquare` 로 로드)
