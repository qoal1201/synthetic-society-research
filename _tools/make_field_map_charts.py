"""분야 지도(field-map.qmd) 차트 생성기.

두 장을 뽑는다:
  images/field-map-terrain.png      — 여섯 지역의 연도별 추이 (§1)
  images/field-map-measurement.png  — 개인 충실도 측정 방법 분포 (§4)

실행: <venv>/bin/python _tools/make_field_map_charts.py  (repo 루트에서)
필요: matplotlib + Pretendard 폰트(사이트 본문 폰트와 통일).
데이터 출처: field-map.qmd §3 지역 카드(연도 추이) · §4 1차 분류표(측정 방법).
지도 갱신 시 아래 데이터만 고치고 재실행한다(차트 규칙: 생성 스크립트를 repo에 보관).
색 규칙(CLAUDE.md): 청록 #0F87A8 = 이 연구 / 적색 #C4443C = 빈자리·경고 / 나머지 회색.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Pretendard"
plt.rcParams["axes.unicode_minus"] = False

TEAL = "#0F87A8"   # 이 연구(개인 충실도)
RED  = "#C4443C"   # 정답 불필요 = 빈자리 후보(경고색)
INK  = "#333333"
MUTE = "#8a8a8a"
OUT  = "images"

# ── 차트 1: 여섯 지역 연도별 추이 ──
years  = [2023, 2024, 2025, 2026]
series = [
    ("생성 에이전트 (오픈월드)", [13, 58, 101, 52]),
    ("대규모 사회 시뮬레이션",   [22, 31, 32, 14]),
    ("비판·검증 방법론",         [15, 37, 38, 17]),
    ("실리콘 샘플링 (집단)",     [5, 18, 24, 23]),
    ("기억·엔진",               [6, 19, 20, 16]),
    ("개인 충실도",             [4, 12, 17, 5]),
]
# 큰 지역일수록 진한 회색 (범례 없이 선 끝 직접 라벨)
grays = ["#555555", "#7a7a7a", "#909090", "#a6a6a6", "#bdbdbd"]
short = {"생성 에이전트 (오픈월드)": "생성 에이전트", "대규모 사회 시뮬레이션": "사회 시뮬레이션",
         "비판·검증 방법론": "비판·검증", "실리콘 샘플링 (집단)": "실리콘 샘플링",
         "기억·엔진": "기억·엔진", "개인 충실도": "개인 충실도"}

fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
ax.axvspan(2025.5, 2026.35, color="#f1f1f1", zorder=0)
ax.text(2025.95, 103, "2026\n부분 집계", color=MUTE, fontsize=9, ha="center", va="top")

line_colors = {}
gi = 0
for name, ys in series:
    if name == "개인 충실도":
        ax.plot(years, ys, color=TEAL, lw=3, marker="o", ms=5, zorder=5)
        line_colors[name] = TEAL
    else:
        c = grays[gi]; gi += 1
        ax.plot(years, ys, color=c, lw=1.5, marker="o", ms=3.5, zorder=3)
        line_colors[name] = c

# 선 끝 직접 라벨 — 겹치면 위에서부터 4.5 간격으로 밀어냄
ends = sorted(((ys[-1], name) for name, ys in series), reverse=True)
prev = float("inf")
for val, name in ends:
    y = min(val, prev - 4.5)
    prev = y
    bold = name == "개인 충실도"
    ax.text(2026.45, y, short[name], color=line_colors[name], fontsize=8.5,
            va="center", weight="bold" if bold else "normal")

ax.set_xticks(years)
ax.set_xlabel("연도", fontsize=11)
ax.set_ylabel("논문 수 (편)", fontsize=11)
ax.set_title("여섯 지역의 연도별 추이 (중복 제거, 649편)", fontsize=13, weight="bold", loc="left")
ax.set_xlim(2022.8, 2027.6)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#eeeeee")
fig.tight_layout()
fig.savefig(f"{OUT}/field-map-terrain.png", facecolor="white", bbox_inches="tight")
plt.close(fig)

# ── 차트 2: 개인 충실도 측정 방법 분포 ──
methods = [
    ("집단 분포 대 실제 데이터", 35, False),
    ("고정 문항 대 개인 정답",   31, False),
    ("고정 벤치마크 정확도",     10, False),
    ("열린 행동의 인간 평가",     22, True),
    ("참조 없는 일관성 채점",     2,  True),
]
labels = [m[0] for m in methods]
vals   = [m[1] for m in methods]
colors = [RED if m[2] else MUTE for m in methods]

fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
ypos = list(range(len(methods)))
ax.barh(ypos, vals, color=colors, height=0.62)
ax.set_yticks(ypos)
ax.set_yticklabels(labels, fontsize=11)
ax.invert_yaxis()
for i, v in enumerate(vals):
    ax.text(v + 0.6, i, str(v), va="center", fontsize=10, color=INK)
ax.set_xlabel("해당 방식으로 잰 논문 수", fontsize=11)
ax.set_title("개인 충실도를 재는 방법 (측정 100편 기준)", fontsize=13, weight="bold", loc="left")
ax.set_xlim(0, 40)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", color="#eeeeee")
ax.set_axisbelow(True)
legend_h = [plt.Rectangle((0, 0), 1, 1, color=MUTE),
            plt.Rectangle((0, 0), 1, 1, color=RED)]
ax.legend(legend_h, ["정답 필요", "정답 불필요 (빈자리 후보)"], fontsize=9, loc="lower right", frameon=False)
fig.tight_layout()
fig.savefig(f"{OUT}/field-map-measurement.png", facecolor="white", bbox_inches="tight")
plt.close(fig)

print("saved: images/field-map-terrain.png, images/field-map-measurement.png")
