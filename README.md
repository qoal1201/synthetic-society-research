# Synthetic Society Research

인간과 AI가 상호작용하는 합성사회(synthetic society)를 공부하고 기록하는 저장소.
관련 연구를 읽고, 비판하고, 작게 재현한다.

읽기 좋은 버전(사이트): https://qoal1201.github.io/synthetic-society-research/

## 구조

| 폴더 / 파일 | 내용 |
|---|---|
| `research-log/` | 날짜별 공부 일지 |
| `paper-reviews/` | 논문 리뷰 — 핵심 주장·방법·한계·문제점 |
| `reproductions/` | 논문 결과 재현 — 코드 + 원논문 대조 |
| `glossary.qmd` | 개념 정리 |
| `open-questions.qmd` | 열린 질문 |

글은 Quarto로 작성하고 GitHub Pages로 배포한다. 재현 코드는 각 `reproductions/<주제>/` 폴더에 실행법과 함께 둔다.

## 재현 실행

각 재현물은 독립 실행 가능한 작은 프로젝트다 — 데이터 사이언스 표준(cookiecutter-data-science)의 축소판:

```
reproductions/<주제>/
  README.qmd        설명 + 원논문 대조
  requirements.txt  파이썬 환경
  src/              재현 코드
  data/             데이터 (raw는 커밋 제외)
```

실행: `pip install -r requirements.txt` 후 각 README의 실행법 참조. (첫 재현: Generative Agents, 준비 중)
