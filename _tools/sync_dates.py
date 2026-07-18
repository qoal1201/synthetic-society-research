#!/usr/bin/env python3
"""리뷰·실험 글의 date-modified를 실제 수정 사실에 맞춘다.

왜 필요한가 — 리뷰는 가든 문서라 발행 후에도 계속 자란다. 상단에 공개일만
찍혀 있으면 "그날 만들고 끝"으로 읽히므로 최종 갱신일을 함께 표시하는데,
이 값을 손으로 관리하면 반드시 어긋난다. 그래서 git이 아는 사실에서 파생시킨다.

동작:
  - 작업 트리에 내용 변경이 있는 문서 → date-modified를 오늘로
  - 그 외 → 내용이 실제로 바뀐 마지막 커밋일로 (없으면 추가)
  - date 이하로 내려가면 date-modified를 지운다 (공개 후 안 고친 글엔 갱신일 없음)

date/date-modified 줄만 바뀐 변경은 '내용 변경'으로 세지 않는다. 이 구분이
없으면 스스로 쓴 갱신일이 다음 실행의 갱신 근거가 되어 날짜가 끝없이 밀린다.

커밋 직전에 돌린다. --check는 고칠 게 있으면 종료코드 1 (CI·훅용).
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET_GLOBS = ("paper-reviews/*.qmd", "experiments/2*.qmd")

DATE_RE = re.compile(r'^date:\s*"([^"]+)"\s*$', re.M)
MODIFIED_RE = re.compile(r'^date-modified:\s*"([^"]+)"\s*\n', re.M)


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()


def dirty_paths():
    """작업 트리에서 내용이 바뀐 추적 파일 (스테이징 포함, repo 루트 기준 경로).

    `git status --porcelain`을 손으로 자르지 않는다 — git()이 출력 전체에 strip을
    걸어 첫 줄의 앞 공백이 사라지는 탓에 첫 항목만 한 글자씩 밀렸다(2026-07-18 실측:
    dirty 파일을 놓치고 '전부 최신'이라 답했다). --name-only는 경로만 내보낸다.
    """
    out = git("diff", "--name-only", "HEAD")
    return {p for p in out.splitlines() if p.strip()}


META_FIELDS = ("date:", "date-modified:")


def diff_has_content(diff):
    """diff에 date/date-modified 줄 말고 실제 내용 변경이 있나."""
    for line in diff.splitlines():
        if line.startswith(("+++", "---", "@@")):
            continue
        if line[:1] in ("+", "-"):
            body = line[1:].strip()
            if body and not body.startswith(META_FIELDS):
                return True
    return False


def last_content_commit_date(rel):
    """독자가 볼 내용이 실제로 바뀐 마지막 커밋일.

    date/date-modified 줄만 바꾼 커밋은 건너뛴다. 안 그러면 이 스크립트가
    쓴 갱신일이 다음 실행 때 또 갱신 근거가 되어 날짜가 끝없이 올라간다
    (2026-07-18 첫 실행에서 실측 — 리뷰 7편이 전부 하루 밀릴 뻔했다).
    """
    created = git("log", "--diff-filter=A", "--pretty=format:%H", "--", rel).splitlines()
    created_sha = created[-1] if created else None

    log = git("log", "--pretty=format:%H %ad", "--date=short", "--", rel)
    for line in log.splitlines():
        sha, _, day = line.partition(" ")
        # 생성 커밋은 '갱신'이 아니다 — 만든 뒤 안 고친 글은 갱신일이 없어야 한다.
        if sha == created_sha:
            break
        diff = git("show", "--format=", "--unified=0", sha, "--", rel)
        if diff_has_content(diff):
            return day
    return ""


def targets():
    for pattern in TARGET_GLOBS:
        yield from sorted(ROOT.glob(pattern))


def main():
    check_only = "--check" in sys.argv
    today = date.today().isoformat()
    dirty = dirty_paths()
    changed = []

    for path in targets():
        rel = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")

        m = DATE_RE.search(text)
        if not m:
            print(f"[건너뜀] {rel} — date 필드 없음")
            continue
        published = m.group(1)

        if rel in dirty and diff_has_content(git("diff", "HEAD", "--", rel)):
            wanted = today
        else:
            wanted = last_content_commit_date(rel) or published

        # 공개 당일에 멈춘 문서는 갱신일을 표시하지 않는다.
        if wanted <= published:
            wanted = None

        cur_m = MODIFIED_RE.search(text)
        current = cur_m.group(1) if cur_m else None
        if current == wanted:
            continue

        if cur_m:
            text = MODIFIED_RE.sub("", text, count=1)
        if wanted:
            text = DATE_RE.sub(
                lambda mm: f'{mm.group(0)}\ndate-modified: "{wanted}"', text, count=1
            )

        changed.append((rel, current, wanted))
        if not check_only:
            path.write_text(text, encoding="utf-8")

    if not changed:
        print("date-modified 전부 최신")
        return 0

    for rel, before, after in changed:
        print(f"{'[확인]' if check_only else '[갱신]'} {rel}: {before or '없음'} → {after or '없음'}")
    return 1 if check_only else 0


if __name__ == "__main__":
    sys.exit(main())
