# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib"]
# ///
"""GA 리뷰(2304.03442) 그림 1장.

  images/ga-two-measures.svg — 같은 논문의 두 측정: 비교군이 있는 통제 평가(왼쪽)
                               vs 비교군이 없는 창발 측정(오른쪽)

데이터 출처: 리뷰 본문 표 그대로 — TrueSkill μ 5조건(29.89/26.88/25.64/22.95/21.21,
논문 §6) · 관계망 밀도 0.167→0.74(§7.1). "인간 vs 완전 제거 쌍만 유의하지 않음"도 본문.
"""
import matplotlib.pyplot as plt

import figstyle
from figstyle import TEAL, RED, INK, MUTE, FAINT

figstyle.apply()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2), width_ratios=[1.45, 1])

# ── 왼쪽: 통제 평가 — 조건 5개가 나란하다 ──
conds = [
    ("전체 아키텍처", 29.89, TEAL),
    ("−reflection", 26.88, MUTE),
    ("−reflection −planning", 25.64, MUTE),
    ("인간 크라우드워커", 22.95, INK),
    ("−memory −planning −reflection", 21.21, MUTE),
]
ypos = range(len(conds))
ax1.barh(ypos, [c[1] for c in conds], color=[c[2] for c in conds], height=0.62)
ax1.set_yticks(list(ypos))
ax1.set_yticklabels([c[0] for c in conds], fontsize=10)
ax1.invert_yaxis()
for i, (_, v, _c) in enumerate(conds):
    ax1.text(v + 0.35, i, f"{v:.2f}", va="center", fontsize=9.5, color=INK)
# 4위·5위 쌍만 통계가 못 가름 (Dunn post-hoc)
ax1.plot([32.6, 33.4, 33.4, 32.6], [3, 3, 4, 4], color=RED, lw=1.1, clip_on=False)
ax1.text(33.9, 3.5, "이 쌍만\n유의 X", va="center", fontsize=9, color=RED)
ax1.set_xlim(0, 33)
ax1.set_xlabel("believability 순위 점수 (TrueSkill μ)", fontsize=10.5)
ax1.set_title("통제 평가 — 비교군 5개, 숫자가 말을 한다", fontsize=12, weight="bold", loc="left")
ax1.spines[["top", "right"]].set_visible(False)
ax1.grid(axis="x", color=figstyle.GRID)
ax1.set_axisbelow(True)

# ── 오른쪽: 창발 측정 — 0.74 옆이 비어 있다 ──
ax2.bar([0], [0.167], 0.55, color=FAINT)
ax2.bar([1], [0.74], 0.55, color=TEAL)
ax2.add_patch(plt.Rectangle((2 - 0.275, 0), 0.55, 0.74, facecolor="none",
                            edgecolor=RED, lw=1.6, ls="--"))
ax2.text(2, 0.36, "?", ha="center", va="center", fontsize=22, color=RED, weight="bold")
ax2.text(0, 0.19, "0.167", ha="center", fontsize=10, color=INK)
ax2.text(1, 0.762, "0.74", ha="center", fontsize=10, color=INK)
ax2.set_xticks([0, 1, 2])
ax2.set_xticklabels(["시작 시각\n(비교군 아님 —\n이틀 효과와 섞임)", "2게임일 뒤\n(전체 아키텍처)", "아키텍처를\n뺀 마을\n(안 돌림)"], fontsize=9.5)
ax2.set_ylabel("관계망 밀도", fontsize=10.5)
ax2.set_ylim(0, 1)
ax2.set_title("창발 측정 — 비교군 없음", fontsize=12, weight="bold", loc="left")
ax2.spines[["top", "right"]].set_visible(False)
ax2.grid(axis="y", color=figstyle.GRID)
ax2.set_axisbelow(True)

fig.tight_layout(w_pad=3)
figstyle.save(fig, "ga-two-measures")
