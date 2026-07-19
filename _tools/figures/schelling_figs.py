# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib"]
# ///
"""Schelling 리뷰(1971) 그림 2장.

  images/schelling-linear-setup.svg — 선형 모델 규칙 모식도(이웃 8명 중 4명)
  images/schelling-baseline.svg     — 무작위 배치 vs 균형 도달, 같은 색 이웃 비율

데이터 출처: 리뷰 본문 표(p.158 — 무작위 영 53%·별 46% / 균형 영 83%·별 80%),
"+30%p = 규칙이 한 일"도 본문 서술 그대로. linear-setup은 규칙 설명용 모식도라
칸 배열은 그림용이지 논문의 실제 초기 배열이 아니다.
"""
import matplotlib.pyplot as plt

import figstyle
from figstyle import TEAL, RED, INK, MUTE, FAINT

figstyle.apply()

# ── 그림 1: 선형 모델 규칙 모식도 ──
# ★=별, 0=영. 초점 인물(i=8) 기준 양옆 4명씩이 이웃 8명.
row = ["0", "★", "0", "0", "★", "0", "★", "0", "★", "0", "0", "★", "0", "0", "★", "★", "0"]
focal = 8  # ★ — 이웃(i4~7, i9~12) 중 같은 색(★)은 i4·i6·i11의 3명 → 불만

fig, ax = plt.subplots(figsize=(8.6, 2.5))
for i, ch in enumerate(row):
    in_nbhd = abs(i - focal) <= 4 and i != focal
    face = "#f1f1f1" if in_nbhd else "white"
    edge = TEAL if i == focal else FAINT
    lw = 2.2 if i == focal else 0.9
    ax.add_patch(plt.Rectangle((i, 0), 0.92, 0.92, facecolor=face, edgecolor=edge, lw=lw))
    ax.text(i + 0.46, 0.44, ch, ha="center", va="center", fontsize=13,
            color=INK if ch == "★" else MUTE, weight="bold" if i == focal else "normal")

ax.annotate("이웃 8명(양옆 4명씩)", xy=(focal + 0.46, 1.06), xytext=(focal + 0.46, 1.75),
            ha="center", fontsize=10.5, color=INK,
            arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.9))
ax.plot([focal - 4, focal + 5 - 0.08], [1.06, 1.06], color=MUTE, lw=1.2)
ax.text(focal + 0.46, -0.42, "나(★) — 이웃 8명 중 같은 색 3명 < 4명 → 불만 → 최소 요구가\n채워지는 가장 가까운 자리로 이동", ha="center", va="top",
        fontsize=10.5, color=TEAL)
ax.set_xlim(-0.3, len(row) + 0.3)
ax.set_ylim(-1.45, 2.0)
ax.axis("off")
figstyle.save(fig, "schelling-linear-setup")

# ── 그림 2: 무작위 배치 vs 균형 도달 (p.158) ──
# 값: 무작위(Fig.7) 영 53%·별 46% / 균형(Fig.9) 영 83%·별 80%
groups = ["무작위 배치", "균형 도달"]
zeros = [53, 83]
stars = [46, 80]

fig, ax = plt.subplots(figsize=(6.4, 4.2))
x = [0, 1]
w = 0.34
b1 = ax.bar([i - w / 2 for i in x], zeros, w, color=[MUTE, TEAL], label="영")
b2 = ax.bar([i + w / 2 for i in x], stars, w, color=[FAINT, "#6fb4c6"], label="별")
for bars in (b1, b2):
    for rect in bars:
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 1.5,
                f"{rect.get_height():.0f}%", ha="center", fontsize=10.5, color=INK)

# 규칙이 한 일 = 53 → 83, +30%p (영 기준, 본문 서술)
ax.annotate("", xy=(1 - w / 2 - 0.03, 80.5), xytext=(0 - w / 2, 53),
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.6,
                            connectionstyle="arc3,rad=-0.25"))
ax.text(0.5, 88, "+30%p = 규칙이 한 일", ha="center", fontsize=11, color=RED, weight="bold")

ax.set_xticks(x)
ax.set_xticklabels(["무작위 배치\n(규칙이 돌기 전)", "균형 도달\n(규칙이 돈 후)"], fontsize=11)
ax.set_ylabel("이웃 중 같은 색 비율 (%)", fontsize=11)
ax.set_ylim(0, 100)
ax.legend(fontsize=10, frameon=False, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color=figstyle.GRID)
ax.set_axisbelow(True)
ax.set_title("같은 격자, 같은 138명 — 다른 것은 규칙이 돌았는지뿐", fontsize=12.5, weight="bold", loc="left")
figstyle.save(fig, "schelling-baseline")
