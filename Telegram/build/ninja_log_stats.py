import argparse
from pathlib import Path


def parse_log(text):
    edges = {}
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) != 5:
            continue
        start, end, _mtime, output, _command = fields
        try:
            start, end = int(start), int(end)
        except ValueError:
            continue
        if end >= start:
            edges[output] = (start, end)
    return edges


def target_of(output):
    # Windows logs mix separators, so a path can read
    # `D:/a/out/CMakeFiles\\Telegram.dir\\main.cpp.obj`.
    parts = output.replace("\\", "/").split("/")
    for part in parts:
        if part.endswith(".dir"):
            return part[:-len(".dir")]
    return parts[-1] if len(parts) == 1 else parts[-2]


def summarize(edges, top=25):
    slowest = sorted(((end - start, output) for output, (start, end) in edges.items()), reverse=True)
    work = sum(duration for duration, _ in slowest)
    span = max(end for _, end in edges.values()) - min(start for start, _ in edges.values())
    targets = {}
    for duration, output in slowest:
        total, count = targets.get(target_of(output), (0, 0))
        targets[target_of(output)] = (total + duration, count + 1)
    return {
        "edges": len(edges),
        "work": work,
        "span": span,
        "parallelism": work / span if span else 0.0,
        "slowest": slowest[:top],
        "targets": sorted(((total, count, name) for name, (total, count) in targets.items()), reverse=True)[:top],
    }


def human(milliseconds):
    seconds = round(milliseconds / 1000, 1)
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, seconds = divmod(round(seconds), 60)
    if minutes < 60:
        return f"{minutes}m {seconds:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02d}m {seconds:02d}s"


def text_report(stats, title):
    lines = [
        f"{title}: {stats['edges']} edges, {human(stats['span'])} wall clock,",
        f"{human(stats['work'])} of compilation at {stats['parallelism']:.2f} average parallelism.",
        "",
        "Slowest targets:",
    ]
    for total, count, name in stats["targets"]:
        lines.append(f"  {human(total):>12}  {count:>5} ×  {name}")
    lines += ["", "Slowest edges:"]
    for duration, output in stats["slowest"]:
        lines.append(f"  {human(duration):>12}  {output}")
    return "\n".join(lines)


def markdown_report(stats, title):
    lines = [
        f"### {title}",
        "",
        f"{stats['edges']} edges, {human(stats['span'])} wall clock, {human(stats['work'])} of compilation, "
        f"{stats['parallelism']:.2f} average parallelism.",
        "",
        "| Target | Edges | Time |",
        "| --- | ---: | ---: |",
    ]
    for total, count, name in stats["targets"]:
        lines.append(f"| `{name}` | {count} | {human(total)} |")
    lines += ["", "| Slowest edge | Time |", "| --- | ---: |"]
    for duration, output in stats["slowest"]:
        lines.append(f"| `{output}` | {human(duration)} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Report build times from a .ninja_log file.")
    parser.add_argument("log", type=Path)
    parser.add_argument("--title", default="Build")
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--markdown-file", type=Path)
    arguments = parser.parse_args(argv)
    if not arguments.log.is_file():
        print(f"{arguments.title}: no {arguments.log} to report.")
        return 0
    edges = parse_log(arguments.log.read_text(errors="replace"))
    if not edges:
        print(f"{arguments.title}: {arguments.log} has no completed edges.")
        return 0
    stats = summarize(edges, arguments.top)
    print(text_report(stats, arguments.title))
    if arguments.markdown_file:
        with arguments.markdown_file.open("a", encoding="utf-8") as summary:
            summary.write(markdown_report(stats, arguments.title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
