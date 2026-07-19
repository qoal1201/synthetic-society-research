"""사이트 공용 차트 스타일 — CLAUDE.md 차트 규칙의 코드화.

색 규칙: 청록 #0F87A8 = 강조 대상(이 연구·측정 주인공) / 적색 #C4443C = 갭·경고 /
나머지 회색. 라벨은 전부 한국어. 폰트 = Pretendard(사이트 본문과 통일).
SVG는 글자를 path로 구워 저장한다 — 방문자 기기에 폰트가 없어도 동일하게 보인다.

사용: 그림 스크립트(같은 폴더)가 `import figstyle` → `figstyle.apply()` →
그린 뒤 `figstyle.save(fig, "이름")`. 출력은 repo 루트 `images/<이름>.svg`.
실행: repo 어디서든 `uv run _tools/figures/<스크립트>.py`.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TEAL = "#0F87A8"   # 강조(측정 주인공)
RED = "#C4443C"    # 갭·경고·빈자리
INK = "#333333"    # 본문 잉크
MUTE = "#8a8a8a"   # 보조 회색
FAINT = "#bdbdbd"  # 옅은 회색
GRID = "#eeeeee"   # 격자선

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "images"


def apply():
    plt.rcParams.update({
        "font.family": "Pretendard",
        "axes.unicode_minus": False,
        "svg.fonttype": "path",  # 글자를 곡선으로 변환 — 폰트 의존 제거
        "figure.dpi": 150,
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
    })


def save(fig, name):
    """images/<name>.svg 저장. 흰 배경 고정 — 다크 테마에서 카드로 읽힌다."""
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{name}.svg"
    fig.savefig(out, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(f"saved: {out.relative_to(ROOT)}")
