# 합성사회 연구 노트

인간과 AI가 상호작용하는 합성사회(synthetic society)를 공부하고 기록하는 저장소.

읽기 좋은 버전(사이트): https://qoal1201.github.io/synthetic-society-research/

## 구조

| 폴더 / 파일 | 내용 |
|---|---|
| `paper-reviews/` | 논문 리뷰 — 해부·판정·한계, 요약이 아님 |
| `experiments/` | 실험 기록 — 실험 하나가 글 하나, 안에 날짜별 체크포인트 |
| `foundations/` | ML 기초 실습 — 캐글 대회 하나가 노트북 하나 |
| `field-map.qmd` | 분야 지도 — 무엇이 연구됐고 어디가 비었나 |
| `glossary.qmd` | 개념 사전 (기초 개념 + 논문별 용어) |
| `reading-list.qmd` | 계보·읽을거리 색인 |
| `index.qmd` | 홈 — 논문·실험 시간순 목록 |

글은 [Quarto](https://quarto.org)로 작성한다. `main`에 푸시하면 GitHub Actions가 렌더해 GitHub Pages로 배포한다(`.github/workflows/publish.yml`).

## 로컬 렌더

```
quarto render
```

결과는 `_site/`에 생성된다. 사이트 정합성 검사는 `python3 _tools/site_lint.py`.

## 메모

- `foundations/`의 노트북은 저장된 실행 결과 그대로 렌더한다. 캐글 대회 데이터(csv)는 재배포 규정상 저장소에 포함하지 않아 재실행되지 않는다.
- 논문 PDF 원본과 정독 노트(`_papers/`)는 저장소에 포함하지 않는다.
