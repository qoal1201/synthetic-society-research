#!/usr/bin/env python3
"""사이트 정합 lint — 공개 qmd의 기계적 결함을 잡는다.

검사 항목:
1. 깨진 파이프 표 — 헤더 구분선 없는 표 블록 (2026-07-07 용어집에서 실측된 버그 클래스:
   표 사이 빈 줄 때문에 뒷부분이 헤더 없는 블록으로 떨어져 파이프 문자가 그대로 렌더됨)
2. 내부 링크 — 로컬 .qmd/.md 링크의 대상 파일 존재 + {#앵커} 존재 (앵커는 경고 수준)
3. 방문자 표면의 내부 운영 용어 — 전 공개 파일 대상 (일지 예외는 2026-07-10 재구조로 폐지)
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
    + sorted((ROOT / "experiments").glob("*.qmd"))
    + sorted((ROOT / "foundations").glob("*.qmd"))
)

# 내부 운영 용어 — 방문자 표면에서 금지 (CLAUDE.md "방문자 표면 vs 운영 용어")
JARGON_ERROR = ["load-bearing", "just-in-time", "작업호", "진실원"]
JARGON_WARN = ["마일스톤", "체크포인트", "BACKLOG"]

# 상단에 "> 상태:" 줄이 있어야 하는 가든 문서
STATUS_REQUIRED = (
    ["glossary.qmd", "field-map.qmd", "reading-list.qmd",
     "experiments/index.qmd", "foundations/index.qmd"]
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


GLOSSARY_MAX_CHARS = 430  # 항목 본문 장황 경고 문턱 (한 줄 정의 + 설명 문단 1개 기준)


def check_glossary():
    """용어집 구조 규칙(2026-07-12 개편) — 골격·중복·장황을 기계로 감시.

    - #### 헤딩엔 {#앵커} 필수, 파일 내 앵커 중복 금지(07-10 창발 중복 실측 클래스)
    - 항목 본문 = 문단 2개(한 줄 정의 + 설명 문단 1개) — 초과는 경고
    - 본문 길이 초과(장황)는 경고 — 넘치는 얘기는 리뷰 본문 몫
    """
    glossary = ROOT / "glossary.qmd"
    if not glossary.exists():
        return
    lines = glossary.read_text(encoding="utf-8").splitlines()
    seen, entries, current = {}, [], None
    for i, line in enumerate(lines, 1):
        if line.startswith("#### "):
            m = ANCHOR_RE.search(line)
            if not m:
                errors.append(f"glossary.qmd:{i} 항목 헤딩에 {{#앵커}} 없음")
            else:
                anchor = m.group(1)
                if anchor in seen:
                    errors.append(f"glossary.qmd:{i} 앵커 중복 {{#{anchor}}} — {seen[anchor]}줄과 충돌")
                seen[anchor] = i
            current = (i, [])
            entries.append(current)
        elif line.startswith(("## ", "### ")):
            current = None
        elif current is not None:
            current[1].append(line)
    for i, body in entries:
        paras = [p for p in "\n".join(body).split("\n\n") if p.strip()]
        if len(paras) > 2:
            warnings.append(f"glossary.qmd:{i} 항목 문단 {len(paras)}개 — 골격은 '한 줄 정의 + 설명 문단 1개'")
        total = sum(len(p) for p in paras)
        if total > GLOSSARY_MAX_CHARS:
            warnings.append(f"glossary.qmd:{i} 항목 본문 {total}자 — 장황 후보({GLOSSARY_MAX_CHARS}자 초과), 리뷰 본문으로 뺄 것 검토")


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
    check_glossary()

    for e in errors:
        print(f"[오류] {e}")
    for w in warnings:
        print(f"[경고] {w}")
    print(f"\n검사 파일 {len(PUBLIC_FILES)}개 · 오류 {len(errors)} · 경고 {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
