import tracemalloc
import linecache
import os


def display_top(snapshot, key_type: str = 'lineno', limit: int = 3) -> str:
    output_lines = []

    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    output_lines.append("Top %s lines" % limit)

    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        output_lines.append("#%s: %s:%s: %.1f KiB"
                            % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            output_lines.append('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        output_lines.append("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    output_lines.append("Total allocated size: %.1f KiB" % (total / 1024))

    return "\n".join(output_lines)
