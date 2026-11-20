"""Render report.html from counts.json for the flow first look (plan Step 3).

Two share charts and a counts table; Chart.js is loaded from cdnjs at a pinned
version and counts.json is inlined. Throwaway script; it is never committed.
"""

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHART_JS = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"
SEGMENTS = ["agent PR", "manual PR", "automated PR", "agent direct", "manual direct"]
READING_LINES = [
    "Signals come only from the D8 p-chart verdicts below; otherwise the answer is \"no signal\". Never read trends by eye.",
    "2026-11 is partial (snapshot 2026-11-20) and is left out of the trend verdicts.",
    "A count is not effort: large and small items count the same.",
    "chore is excluded only for direct commits; the 4 chore PRs are counted.",
    "Rework counts are candidates: fixes also repair external breakage.",
    "Discarded counts closed, unmerged PRs only: a lower bound, counted, not judged.",
]


def main():
    counts = json.loads((HERE / "counts.json").read_text())
    (HERE / "report.html").write_text(_page(counts))
    print(f"wrote {HERE / 'report.html'}")


def _page(counts):
    data = json.dumps(_chart_data(counts))
    table = _table(counts)
    verdicts = "".join(_verdict_item(name, series) for name, series in counts["d8"].items())
    reading = "".join(f"<li>{html.escape(line)}</li>" for line in READING_LINES)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Flow First Look</title>
<style>
:root {{ --bg:#ffffff; --fg:#1d1d1f; --muted:#5f6368; --line:#d9d9de; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#16171a; --fg:#e8e8ea; --muted:#a0a3a8; --line:#33353a; }} }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.45 system-ui,sans-serif; margin:0 auto; max-width:1100px; padding:16px; }}
h1 {{ font-size:22px; }} h2 {{ font-size:17px; margin-top:28px; }}
.muted {{ color:var(--muted); }} .chart {{ position:relative; height:340px; }}
table {{ border-collapse:collapse; width:100%; font-size:13px; display:block; overflow-x:auto; }}
th,td {{ border-bottom:1px solid var(--line); padding:4px 6px; text-align:right; white-space:nowrap; }}
th:first-child,td:first-child {{ text-align:left; }}
</style>
<script src="{CHART_JS}"></script></head><body>
<h1>Flow first look: where delivered work flows</h1>
<h2>What this page shows</h2>
<p>This repository automates how my machines are built (Ansible). I build it together with AI coding agents, and I also use it
as a lab for learning how to work with agents. This page looks back at the work that was <b>delivered</b> each month and asks
where it went:</p>
<ul>
<li><b>Machines:</b> work on the machine automation itself (roles, playbooks, CI, scripts).</li>
<li><b>Lab:</b> work on how the agents work: their rules, skills and settings (for example <code>.claude/</code>,
<code>AGENTS.md</code>).</li>
<li><b>Rework:</b> fixes and reverts of earlier delivered work. This is <i>failure demand</i>: work that exists only because
earlier work was not right.</li>
<li><b>Automated:</b> dependency updates opened by Dependabot. <b>Discarded:</b> pull requests closed without merging.</li>
</ul>
<p>"Delivered" means a pull request merged into <code>main</code>, or a commit made directly on <code>main</code>. Every
item counts once, whatever its size. A change is sorted into machines or lab by the majority of the files it touches; a title
starting with "fix", "bug" or "revert" makes it rework. Data covers 2026-04-01 to 2026-11-20 (git snapshot 0455604). Earlier
months are left out, because before April most work went straight to <code>main</code> and the counts are not comparable.</p>
<p>The question behind it: my own attention is probably the bottleneck of this way of working, and rework probably eats a
large part of it. This first look tests the cheap part of that idea with data that already exists.</p>
<h2>How to read</h2><ul>{reading}</ul>
<h2>Chart 1: machines, lab and rework as shares of delivered non-automated items</h2>
<p class="muted">n above each bar. Hatched months have n &lt; 5: too small to read. Automated and discarded are counts in the table, outside the base.</p>
<div class="chart"><canvas id="chart1"></canvas></div>
<h2>Chart 2: delivered items by author and channel, as shares</h2>
<p class="muted">n above each bar = all delivered items in the month. "manual" = opened or committed by the owner by hand.</p>
<div class="chart"><canvas id="chart2"></canvas></div>
<h2>Is anything changing? Trend verdicts</h2>
<p>Monthly shares jump around by chance, especially in months with few items. To avoid reading a trend into noise, each share
is judged by a fixed rule chosen before looking at the data: a <b>p-chart</b> (Wheeler). It computes the average share over all
readable months (p&#772;) and, for each month, a band of normal variation that is wider when the month has fewer items.
<b>A real change shows as a month outside its band</b>, or as 6 rises or 6 falls in a row. Anything else is "no signal": the
months differ, but not more than chance would explain. Only full months with at least 5 items are read (2026-04 to 2026-10);
the 6-in-a-row rule needs at least 7 such months.</p>
<ul>{verdicts}</ul>
<h2>Counts per month</h2>
<p>One row per month. <b>machines, lab, rework</b> are the delivered items in Chart 1; <b>base n</b> is their sum, the base of
the shares. <b>automated</b> are merged Dependabot pull requests; <b>discarded</b> are pull requests closed without merging;
<b>closed Dependabot</b> are superseded Dependabot updates. The five author columns split all delivered items by who opened
the pull request (or authored the direct commit): "agent" is an AI coding agent, "manual" is me. Git cannot fully separate my
work from interactive agent work, so read these columns as "who opened it", not "who did the work". <b>median commits / PR</b>
shows how big pull requests were; it guards against more pull requests appearing only because they got smaller.</p>
{table}
<script>
const DATA = {data};
const CSS = getComputedStyle(document.documentElement);
const FG = CSS.getPropertyValue('--fg').trim(), MUTED = CSS.getPropertyValue('--muted').trim();
function hatch(color) {{
  const c = document.createElement('canvas'); c.width = c.height = 8;
  const x = c.getContext('2d'); x.fillStyle = color; x.globalAlpha = 0.35; x.fillRect(0, 0, 8, 8);
  x.globalAlpha = 1; x.strokeStyle = color; x.lineWidth = 2; x.beginPath(); x.moveTo(0, 8); x.lineTo(8, 0); x.stroke();
  return x.createPattern(c, 'repeat');
}}
const nLabels = {{ id: 'nLabels', afterDatasetsDraw(chart) {{
  const ctx = chart.ctx, meta = chart.getDatasetMeta(chart.data.datasets.length - 1);
  ctx.save(); ctx.fillStyle = MUTED; ctx.font = '12px system-ui'; ctx.textAlign = 'center';
  chart.options.nValues.forEach((n, i) => {{ const bar = meta.data[i]; ctx.fillText('n=' + n, bar.x, chart.chartArea.top - 6); }});
  ctx.restore(); }} }};
function shareChart(id, spec) {{
  new Chart(document.getElementById(id), {{ type: 'bar', plugins: [nLabels],
    data: {{ labels: DATA.labels, datasets: spec.series.map(s => ({{ label: s.label,
      data: s.values.map((v, i) => spec.n[i] === 0 ? 0 : 100 * v / spec.n[i]),
      backgroundColor: spec.n.map(n => n < 5 ? hatch(s.color) : s.color) }})) }},
    options: {{ nValues: spec.n, maintainAspectRatio: false, layout: {{ padding: {{ top: 18 }} }},
      plugins: {{ legend: {{ labels: {{ color: FG }} }},
        tooltip: {{ callbacks: {{ label: c => `${{c.dataset.label}}: ${{c.parsed.y.toFixed(0)}}% (${{spec.series[c.datasetIndex].values[c.dataIndex]}} of ${{spec.n[c.dataIndex]}})` }} }} }},
      scales: {{ x: {{ stacked: true, ticks: {{ color: FG }} }},
        y: {{ stacked: true, max: 100, ticks: {{ color: FG, callback: v => v + '%' }} }} }} }} }});
}}
shareChart('chart1', DATA.chart1); shareChart('chart2', DATA.chart2);
</script></body></html>
"""


SERIES_TEXT = {
    "rework_share": ("Rework share", "rework items among all delivered non-automated items",
                     "Is rework (failure demand) growing or shrinking?"),
    "manual_share": ("My share", "items I opened or committed among all delivered non-automated items",
                     "Am I opening or committing less of the work myself?"),
    "agent_rework_share": ("Agent rework share", "rework items among the items agents opened or committed",
                           "Does handing work to agents come back as rework? (the balancing check for my share)"),
}


def _verdict_item(name, series):
    title, base, question = SERIES_TEXT[name]
    readable = [entry["month"] for entry in series["months"]]
    numerator = sum(entry["num"] for entry in series["months"])
    total = sum(entry["n"] for entry in series["months"])
    verdict = ("no signal: every readable month stays inside its band" if series["signals"] == []
               else "signal: " + "; ".join(series["signals"]))
    run_rule = ("the 6-in-a-row rule could fire" if series["run_rule_possible"]
                else f"the 6-in-a-row rule could not fire with only {len(readable)} readable months")
    flagged = ", ".join(series["flagged"]) or "none"
    return (f"<li><b>{html.escape(title)}</b>: {html.escape(question)} The share counts {html.escape(base)}. "
            f"Average p&#772; = {series['p_bar']:.1%} ({numerator} of {total}). Verdict: <b>{html.escape(verdict)}</b>; "
            f"{html.escape(run_rule)}. Months too small to read: {html.escape(flagged)}.</li>")


def _chart_data(counts):
    months = counts["months"]
    labels = [month + (" (partial)" if month == counts["partial_month"] else "") for month in months]
    rows = counts["month_category"]
    chart1 = {
        "n": [rows[month]["base_n"] for month in months],
        "series": [
            {"label": "machines", "color": "#4C78A8", "values": [rows[month]["machines"] for month in months]},
            {"label": "lab", "color": "#54A24B", "values": [rows[month]["lab"] for month in months]},
            {"label": "rework", "color": "#E45756", "values": [rows[month]["rework"] for month in months]},
        ],
    }
    segments = counts["month_segments"]
    colors = ["#4C78A8", "#F58518", "#9D755D", "#72B7B2", "#EECA3B"]
    chart2 = {
        "n": [sum(segments[month].values()) for month in months],
        "series": [
            {"label": segment, "color": color, "values": [segments[month].get(segment, 0) for month in months]}
            for segment, color in zip(SEGMENTS, colors, strict=True)
        ],
    }
    return {"labels": labels, "chart1": chart1, "chart2": chart2}


def _table(counts):
    header = (["month", "machines", "lab", "rework", "base n", "automated", "discarded", "closed Dependabot"]
              + SEGMENTS + ["median commits / PR"])
    lines = ["<table><tr>" + "".join(f"<th>{html.escape(cell)}</th>" for cell in header) + "</tr>"]
    for month in counts["months"]:
        row = counts["month_category"][month]
        discarded = counts["month_discarded"][month]
        segments = counts["month_segments"][month]
        median = counts["median_commits_per_pr"][month]
        cells = ([month, row["machines"], row["lab"], row["rework"], row["base_n"], row["automated"],
                  discarded.get("discarded", 0), discarded.get("closed_dependabot", 0)]
                 + [segments.get(segment, 0) for segment in SEGMENTS]
                 + ["" if median is None else f"{median:g}"])
        lines.append("<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in cells) + "</tr>")
    lines.append("</table>")

    # Rework split, bumps and category x author below the monthly table
    split = counts["rework_split"]
    bumps = counts["bumps_by_author"]
    category_author = counts["category_author"]
    extra = [
        f"Rework split by path vote: lab {split.get('lab', 0)}, machines {split.get('machines', 0)}.",
        "Version bumps by author type: " + ", ".join(f"{k} {v}" for k, v in sorted(bumps.items())) + ".",
        "Category x author: " + "; ".join(
            f"{kind}: " + ", ".join(f"{k} {v}" for k, v in sorted(row.items())) for kind, row in category_author.items()
        ) + ".",
    ]
    return "\n".join(lines) + "<ul>" + "".join(f"<li>{html.escape(line)}</li>" for line in extra) + "</ul>"


if __name__ == "__main__":
    main()
