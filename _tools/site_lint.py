#!/usr/bin/env python3
"""사이트 정합 lint — 공개 qmd의 기계적 결함을 잡는다.

검사 항목:
1. 깨진 파이프 표 — 헤더 구분선 없는 표 블록 (2026-07-07 용어집에서 실측된 버그 클래스:
   표 사이 빈 줄 때문에 뒷부분이 헤더 없는 블록으로 떨어져 파이프 문자가 그대로 렌더됨)
2. 내부 링크 — 로컬 .qmd/.md 링크의 대상 파일 존재 + {#앵커} 존재 (앵커는 경고 수준)
3. 방문자 표면의 내부 운영 용어 — research-log(일지)는 제외 (일지 본문 안에서는 허용 규칙)
4. 가든 문서 상단 상태 줄 존재

사용: python3 _tools/site_lint.py  (repo 어디서든)
종료 코드: 오류(error)가 있으면 1, 경고만 있으면 0
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# _quarto.yml render 목록과 동기화된 공개 파일 집합
PUBLIC_FILES = (
    sorted(ROOT.glob("*.qmd"))
    + sorted((ROOT / "paper-reviews").glob("*.qmd"))
    + sorted(p for p in (ROOT / "research-log").glob("*.qmd") if p.name != "index.qmd")
    + sorted((ROOT / "foundations").glob("*.qmd"))
)

# 내부 운영 용어 — 일지(research-log) 밖 방문자 표면에서 금지 (CLAUDE.md "방문자 표면 vs 운영 용어")
JARGON_ERROR = ["load-bearing", "just-in-time", "작업호", "진실원"]
JARGON_WARN = ["마일스톤", "체크포인트", "BACKLOG"]

# 상단에 "> 상태:" 줄이 있어야 하는 가든 문서
STATUS_REQUIRED = (
    ["glossary.qmd", "field-map.qmd", "clonie-comparison.qmd", "reading-list.qmd",
     "open-questions.qmd", "foundations/index.qmd"]
    + [str(p.relative_to(ROOT)) for p in (ROOT / "paper-reviews").glob("*.qmd")
       if p.name != "index.qmd"]
)

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SEP_ROW_RE = re.compile(r"^\|?[\s:\-|]+\|?$")
ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9_-]+)\}")

errors, warnings = [], []


def strip_code_fences(lines):
    """코드 펜스(```) 안 여부를 라인별 bool 리스트로 반환."""
    in_fence, flags = False, []
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            flags.append(True)
        else:
            flags.append(in_fence)
    return flags


def check_tables(path, lines, fenced):
    block, start = [], None
    def flush():
        nonlocal block, start
        if block:
            if len(block) < 2 or not SEP_ROW_RE.match(block[1].strip()):
                errors.append(f"{path}:{start} 깨진 표 블록(헤더 구분선 없음, {len(block)}줄) — 앞 표와 빈 줄로 분리됐는지 확인")
            block, start = [], None
    for i, line in enumerate(lines, 1):
        if not fenced[i - 1] and line.strip().startswith("|") and line.strip() != "|":
            if not block:
                start = i
            block.append(line)
        else:
            flush()
    flush()


def anchor_targets(path):
    """대상 파일의 명시적 {#id} + 헤딩 근사 슬러그 집합."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return set()
    ids = set(ANCHOR_RE.findall(text))
    for h in re.findall(r"^#+\s+(.+)$", text, re.M):
        h = re.sub(r"[*_`\[\]()]", "", h)
        slug = re.sub(r"[^\w\s가-힣·-]", "", h.lower()).strip()
        ids.add(re.sub(r"[\s·]+", "-", slug))
    return ids


def check_links(path, text):
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("#"):
            frag, file_part = target[1:], str(path)
            resolved = path
        else:
            file_part, _, frag = target.partition("#")
            resolved = (path.parent / file_part).resolve()
            if resolved.suffix not in (".qmd", ".md"):
                continue
            if not resolved.exists():
                errors.append(f"{path} 깨진 링크: ({target}) — 대상 파일 없음")
                continue
        if frag and frag not in anchor_targets(resolved):
            warnings.append(f"{path} 앵커 미확인: ({target}) — 대상에 {{#{frag}}} 없음(헤딩 자동 앵커면 오탐일 수 있음)")


def check_jargon(path, lines, fenced):
    if "research-log" in str(path):
        return
    for i, line in enumerate(lines, 1):
        if fenced[i - 1]:
            continue
        for term in JARGON_ERROR:
            if term in line:
                errors.append(f"{path}:{i} 내부 용어 '{term}' — 방문자 표면에서는 풀어쓸 것")
        for term in JARGON_WARN:
            if term in line:
                warnings.append(f"{path}:{i} 운영 용어 '{term}' — 일지 밖 사용이 맞는지 확인")


def check_status_line(path, lines):
    rel = str(path.relative_to(ROOT))
    if rel in STATUS_REQUIRED:
        head = "\n".join(lines[:20])
        if "> 상태" not in head:
            warnings.append(f"{rel} 가든 문서인데 상단 '> 상태:' 줄이 없음")


def table_rows(text, score_header):
    """파이프 표에서 {첫 셀: 점수 셀} 추출. 헤더에서 score_header 열 위치를 찾는다."""
    rows, score_idx = {}, None
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if score_header in cells:
            score_idx = cells.index(score_header)
            continue
        if score_idx is not None and cells and not set(cells[0]) <= set(":- "):
            if len(cells) > score_idx:
                rows[cells[0]] = cells[score_idx]
    return rows


def check_kaggle_sync():
    """foundations 대회 표 ↔ kaggle README 점수 동기 (진실원 = kaggle README).

    2026-07-07 실측: S6E7 점수 0.86217이 foundations 표에 누락돼 있던 드리프트를 이 대조로 발견.
    kaggle repo가 없는 환경(예: 클론만 받은 외부)에서는 조용히 건너뛴다.
    """
    kaggle_readme = ROOT.parent / "kaggle" / "README.md"
    foundations = ROOT / "foundations" / "index.qmd"
    if not kaggle_readme.exists() or not foundations.exists():
        return
    f_rows = table_rows(foundations.read_text(encoding="utf-8"), "최고 점수")
    k_rows = table_rows(kaggle_readme.read_text(encoding="utf-8"), "최고 점수")
    for name, k_score in k_rows.items():
        if name not in f_rows:
            warnings.append(f"foundations/index.qmd 표에 kaggle README의 '{name}' 행이 없음")
        elif f_rows[name] != k_score:
            errors.append(f"foundations/index.qmd '{name}' 점수 '{f_rows[name]}' ≠ kaggle README '{k_score}' (진실원=kaggle README)")


def main():
    for path in PUBLIC_FILES:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        fenced = strip_code_fences(lines)
        check_tables(path.relative_to(ROOT), lines, fenced)
        check_links(path, text)
        check_jargon(path.relative_to(ROOT), lines, fenced)
        check_status_line(path, lines)

    check_kaggle_sync()

    for e in errors:
        print(f"[오류] {e}")
    for w in warnings:
        print(f"[경고] {w}")
    print(f"\n검사 파일 {len(PUBLIC_FILES)}개 · 오류 {len(errors)} · 경고 {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
