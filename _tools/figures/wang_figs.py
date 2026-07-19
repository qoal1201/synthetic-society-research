# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib"]
# ///
"""wang 리뷰(2402.01908) 그림 2장.

  images/wang-design.svg    — 세 무더기 설계 모식도(기준선 둘 사이 어디에 착지하나)
  images/wang-coverage.svg  — 평탄화: 100개 응답이 커버한 5점 척도 보기 수

데이터 출처: 리뷰 본문에 이미 있는 수치만 쓴다(사람 5개 전부 / GPT-4·3.5는 3개,
논문 p.6). wang-design은 수치 없는 모식도다 — 점 배치는 그림용 배열이지 데이터가 아니다.
"""
import random

import matplotlib.pyplot as plt

import figstyle
from figstyle import TEAL, RED, INK, MUTE, FAINT

figstyle.apply()

# ── 그림 1: 세 무더기 설계 모식도 ──
rng = random.Random(7)  # 고정 시드 — 재실행해도 같은 그림

fig, ax = plt.subplots(figsize=(8, 3.6))

def cluster(cx, cy, n, color, spread=0.07):
    xs = [min(max(cx + rng.gauss(0, spread), cx - 0.14), cx + 0.14) for _ in range(n)]
    ys = [min(max(cy + rng.gauss(0, spread * 0.6), 0.36), 0.66) for _ in range(n)]
    ax.scatter(xs, ys, s=22, color=color, alpha=0.75, linewidths=0, zorder=3)

cluster(0.16, 0.5, 40, INK)    # 내집단(당사자)
cluster(0.84, 0.5, 40, MUTE)   # 외집단 모사
llm = (0.62, 0.5)
ax.scatter(*llm, s=180, color=TEAL, marker="D", zorder=5)
ax.text(llm[0], 0.615, "LLM 응답 100개", color=TEAL, fontsize=11, ha="center", weight="bold")

ax.text(0.16, 0.245, "내집단 100명\n(진짜 당사자)", color=INK, fontsize=10.5, ha="center")
ax.text(0.84, 0.245, "외집단 모사 100명\n(남이 그 정체성인 척)", color=MUTE, fontsize=10.5, ha="center")

# 거리 화살표 — 어느 쪽에 가까운가
ax.annotate("", xy=(0.245, 0.5), xytext=(0.585, 0.5),
            arrowprops=dict(arrowstyle="<->", color=FAINT, lw=1.4))
ax.annotate("", xy=(0.655, 0.5), xytext=(0.755, 0.5),
            arrowprops=dict(arrowstyle="<->", color=INK, lw=1.6))
ax.text(0.415, 0.545, "먼가?", color=MUTE, fontsize=10, ha="center")
ax.text(0.705, 0.545, "가까운가?", color=INK, fontsize=10, ha="center")

ax.text(0.5, 0.87, "기준선이 둘이라 물음이 “얼마나 멀리”에서 “어느 쪽으로”로 바뀐다",
        fontsize=11.5, ha="center", color=INK)

ax.set_xlim(0, 1)
ax.set_ylim(0.15, 0.95)
ax.axis("off")
figstyle.save(fig, "wang-design")

# ── 그림 2: 평탄화 — 커버한 보기 수 ──
rows = [("사람 100명", 5, INK), ("GPT-4", 3, RED), ("GPT-3.5", 3, RED)]

fig, ax = plt.subplots(figsize=(7, 2.6))
ypos = range(len(rows))
ax.barh(ypos, [r[1] for r in rows], color=[r[2] for r in rows], height=0.55)
ax.set_yticks(list(ypos))
ax.set_yticklabels([r[0] for r in rows], fontsize=11)
ax.invert_yaxis()
for i, (_, v, c) in enumerate(rows):
    ax.text(v + 0.07, i, str(v), va="center", fontsize=11, color=c)
ax.axvline(5, color=FAINT, lw=1, ls="--")
ax.text(4.97, -0.62, "보기 전부 = 5", color=MUTE, fontsize=9.5, ha="right")
ax.set_xlim(0, 5.6)
ax.set_xticks(range(6))
ax.set_xlabel("100개 응답이 커버한 5점 척도 보기 수", fontsize=11)
ax.spines[["top", "right"]].set_visible(False)
figstyle.save(fig, "wang-coverage")
