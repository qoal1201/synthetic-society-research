# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib"]
# ///
"""self-report 리뷰(2411.10109) 그림 2장.

  images/self-report-tasks.svg       — 세 과제 × 5에이전트 정규화 정확도 막대
  images/self-report-normalized.svg  — 정규화 개념도(원시 ÷ 그 사람 천장 = 정규화)

데이터 출처: 리뷰 본문 평가 표의 수치만 쓴다(원문 Table 8 대조 완료).
  GSS 0.83/0.82/0.86/0.74/0.71 · Big Five 0.80/0.65/0.77/0.61/0.75 ·
  경제 게임 0.66/0.38/0.49/0.48/0.57 (인터뷰/설문/결합/인구통계/페르소나).
  정규화 개념도의 65.67·79.53·0.83은 GSS 헤드라인(본문 §정규화 정확도).
self-report-normalized는 개념도다 — 막대 폭·배치는 설명용이지 데이터가 아니다.
"""
import matplotlib.pyplot as plt

import figstyle
from figstyle import TEAL, RED, INK, MUTE, FAINT, GRID

figstyle.apply()

# ── 그림 1: 세 과제 × 5에이전트 정규화 정확도 ──
tasks = ["GSS\n(태도)", "Big Five\n(성격)", "경제 게임\n(행동)"]
# 자기보고 3(청록 톤) vs 베이스라인 2(회색) — 색으로 두 무리를 가른다
agents = [
    ("인터뷰",   [0.83, 0.80, 0.66], TEAL,  1.0),
    ("설문",     [0.82, 0.65, 0.38], TEAL,  0.62),
    ("결합",     [0.86, 0.77, 0.49], TEAL,  0.38),
    ("인구통계", [0.74, 0.61, 0.48], MUTE,  1.0),
    ("페르소나", [0.71, 0.75, 0.57], FAINT, 1.0),
]

fig, ax = plt.subplots(figsize=(8, 4))
xpos = [0, 1, 2]
width = 0.16
offsets = [-2, -1, 0, 1, 2]
for (name, vals, color, alpha), off in zip(agents, offsets):
    xs = [xi + off * width for xi in xpos]
    ax.bar(xs, vals, width, color=color, alpha=alpha, label=name, zorder=3)

ax.set_xticks(xpos)
ax.set_xticklabels(tasks, fontsize=11)
ax.set_ylim(0, 1.0)
ax.set_ylabel("정규화 정확도 (그 사람 천장 대비)", fontsize=10.5)
ax.axhline(1.0, color=FAINT, lw=1, ls="--")
ax.text(2.42, 1.01, "천장 = 1.0", color=MUTE, fontsize=9, ha="right", va="bottom")
ax.legend(ncol=5, fontsize=9.5, loc="upper center", bbox_to_anchor=(0.5, -0.11),
          frameon=False, columnspacing=1.2, handlelength=1.1)
ax.spines[["top", "right"]].set_visible(False)
ax.set_axisbelow(True)
ax.yaxis.grid(True, color=GRID, lw=1)
ax.set_title("자기보고(청록)가 얕은 베이스라인(회색)을 앞서지만,\n경제 게임에선 그 우위가 흐려진다",
             fontsize=11.5, color=INK, pad=12)
figstyle.save(fig, "self-report-tasks")

# ── 그림 2: 정규화 개념도 (원시 ÷ 천장 = 정규화) ──
# GSS 헤드라인: 원시 65.67% ÷ 천장 79.53% = 정규화 0.83. 개념도.
fig, ax = plt.subplots(figsize=(6, 4.2))

# 왼쪽 기둥: 실제 척도 0~100. 천장까지 옅게 채우고, 원시 지점을 청록으로.
bx = 0.0
ax.bar([bx], [100], width=0.5, color="white", edgecolor=FAINT, lw=1, zorder=1)
ax.bar([bx], [79.53], width=0.5, color=GRID, zorder=2)
ax.bar([bx], [65.67], width=0.5, color=TEAL, alpha=0.85, zorder=3)

# 세 기준선
ax.text(bx, 65.67 - 4, "에이전트 원시\n65.67%", color="white", fontsize=9.5,
        ha="center", va="top", weight="bold", zorder=4)
ax.annotate("그 사람 천장 79.53%\n(2주 뒤 자기 재현율)", xy=(bx + 0.25, 79.53),
            xytext=(bx + 0.62, 82), fontsize=9.5, color=INK, va="center",
            arrowprops=dict(arrowstyle="-", color=INK, lw=1))
ax.annotate("원래 만점 100\n(아무도 못 닿음)", xy=(bx + 0.25, 100),
            xytext=(bx + 0.62, 99), fontsize=9, color=MUTE, va="center",
            arrowprops=dict(arrowstyle="-", color=FAINT, lw=1))

# 나눗셈 식
ax.text(bx + 0.5, 40,
        "만점을 100이 아니라\n그 사람 천장으로 바꾼다\n\n65.67 ÷ 79.53 = 0.83",
        fontsize=10.5, color=INK, ha="center", va="center")

ax.set_xlim(-0.5, 1.6)
ax.set_ylim(0, 108)
ax.set_ylabel("실제 정확도 (%)", fontsize=10.5)
ax.set_xticks([])
ax.spines[["top", "right", "bottom"]].set_visible(False)
figstyle.save(fig, "self-report-normalized")
