from pathlib import Path

# ---------- Directories ----------
# Paths for raw PDFs, structured JSON, and raw JSON tables
dirs = {
    "Raw PDFs": {
        "Chapter PDFs": "pdf/chapters",
        "General Notes PDFs": "pdf/general_notes"
    },
    "Raw JSON": {
        "Tables": "json/tables"
    },
    "Structured JSON": {
        "General Notes": "data/notes/general",
        "Additional Notes": "data/notes/additional",
        "Chapter Notes": "data/notes/chapter",
        "Section Notes": "data/notes/section",
        "Tables": "data/tables"
    }
}

# ---------- Sample chapters per cumulative structured JSON ----------
# Used to calculate per-chapter size for projections
sample_chapters = {
    "General Notes": 18,
    "Additional Notes": 15,
    "Chapter Notes": 18,
    "Section Notes": 3,
    "Tables": 18
}

# ---------- Total chapters for projection ----------
# Total number of chapters in the full HTS
total_chapters = {
    "General Notes": 36,
    "Additional Notes": 99,
    "Chapter Notes": 99,
    "Section Notes": 22,
    "Tables": 99
}

# ---------- Helper Functions ----------

def get_file_stats(directory):
    """
    Collect file statistics in a directory.
    
    Parameters:
        directory (str or Path): Path to the directory to scan.
        
    Returns:
        tuple: (total_size, count, avg_size, min_size, max_size)
            - total_size (int): Sum of all file sizes in bytes.
            - count (int): Number of files.
            - avg_size (float): Average file size in bytes.
            - min_size (int): Smallest file size in bytes.
            - max_size (int): Largest file size in bytes.
    
    Notes:
        - Only considers regular files, ignores subdirectories.
        - Returns zeros if directory doesn't exist or contains no files.
    """
    sizes = []
    p = Path(directory)
    if not p.exists():
        return 0, 0, 0, 0, 0
    for f in p.glob("*"):
        if f.is_file():
            sizes.append(f.stat().st_size)
    if not sizes:
        return 0, 0, 0, 0, 0
    total_size = sum(sizes)
    count = len(sizes)
    avg_size = total_size / count
    min_size = min(sizes)
    max_size = max(sizes)
    return total_size, count, avg_size, min_size, max_size

def sizeof_fmt(num, suffix='B'):
    """
    Convert a byte count into a human-readable format (e.g., KB, MB, GB).

    Parameters:
        num (int or float): Size in bytes.
        suffix (str): Suffix to append (default 'B').
    
    Returns:
        str: Human-readable file size.
    
    Example:
        sizeof_fmt(2048) -> '2.0 KB'
    """
    for unit in ['','K','M','G','T']:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"

def calc_ratio(stage1, stage2):
    """
    Calculate expansion ratio from stage1 → stage2.

    Parameters:
        stage1 (int or float): Initial size (e.g., raw PDF total size).
        stage2 (int or float): Subsequent size (e.g., structured JSON total size).
    
    Returns:
        float: Expansion ratio (stage2 / stage1). Returns 0 if stage1 is 0.
    
    """
    if stage1 == 0:
        return 0
    return stage2 / stage1

# ---------- Collect Data ----------
# Collect stats for all directories (count, total, avg, min, max)
data_summary = {}
for category, subdirs in dirs.items():
    data_summary[category] = {}
    for name, path in subdirs.items():
        total, count, avg, min_size, max_size = get_file_stats(path)
        data_summary[category][name] = {
            "count": count,
            "total_size": total,
            "avg_size": avg,
            "min_size": min_size,
            "max_size": max_size
        }

# ---------- Calculate Expansion Ratios ----------
pdf_chapter_total = data_summary["Raw PDFs"]["Chapter PDFs"]["total_size"]
json_chapter_total = (
    data_summary["Structured JSON"]["Chapter Notes"]["total_size"] +
    data_summary["Structured JSON"]["Section Notes"]["total_size"] +
    data_summary["Structured JSON"]["Additional Notes"]["total_size"]
)
ratio_pdf_to_json = calc_ratio(pdf_chapter_total, json_chapter_total)

pdf_general_total = data_summary["Raw PDFs"]["General Notes PDFs"]["total_size"]
json_general_total = data_summary["Structured JSON"]["General Notes"]["total_size"]
ratio_pdf_to_json_general = calc_ratio(pdf_general_total, json_general_total)

raw_json_total = data_summary["Raw JSON"]["Tables"]["total_size"]
structured_json_tables_total = data_summary["Structured JSON"]["Tables"]["total_size"]
ratio_json_to_struct = calc_ratio(raw_json_total, structured_json_tables_total)

# ---------- Project Full HTS Storage ----------
raw_projected = []
structured_projected = []
total_bytes = 0

# --- Raw PDFs and Raw JSON Tables ---
# Project size linearly based on total chapters/tables
proj_chapter_raw = pdf_chapter_total * total_chapters["Chapter Notes"] / sample_chapters["Chapter Notes"]
proj_general_raw = pdf_general_total * total_chapters["General Notes"] / sample_chapters["General Notes"]
proj_json_raw = raw_json_total * total_chapters["Tables"] / sample_chapters["Tables"]

raw_projected.append(f"- **Chapter PDFs:** Projected Size: {sizeof_fmt(proj_chapter_raw)} (based on 99 chapters)")
raw_projected.append(f"- **General Notes PDFs:** Projected Size: {sizeof_fmt(proj_general_raw)} (based on 36 chapters)")
raw_projected.append(f"- **Raw JSON Tables:** Projected Size: {sizeof_fmt(proj_json_raw)} (based on 99 chapters)")

total_bytes += proj_chapter_raw + proj_general_raw + proj_json_raw

# --- Cumulative Structured JSON ---
# Use average size per sample chapter × total chapters
for name, sample_count in sample_chapters.items():
    total_count = total_chapters.get(name, sample_count)
    total_size = data_summary["Structured JSON"].get(name, {}).get("total_size", 0)
    if total_size > 0 and sample_count > 0:
        avg_per_chapter = total_size / sample_count
        projected_size = avg_per_chapter * total_count
        structured_projected.append(f"- **{name}:** Projected Size: {sizeof_fmt(projected_size)} "
                                    f"(based on {total_count} chapters, ~{sizeof_fmt(avg_per_chapter)} per chapter)")
        total_bytes += projected_size
    else:
        structured_projected.append(f"- **{name}:** No data to project")

# ---------- Generate Markdown Report ----------
report_lines = ["# HTS Data Size Report\n"]

# --- File counts, totals, averages, min/max ---
for category, files in data_summary.items():
    report_lines.append(f"## {category}\n")
    for name, info in files.items():
        report_lines.append(f"- **{name}**")
        report_lines.append(f"  - File Count: {info['count']}")
        report_lines.append(f"  - Total Size: {sizeof_fmt(info['total_size'])}")
        report_lines.append(f"  - Average Size: {sizeof_fmt(info['avg_size'])}")
        if category != "Structured JSON":  # min/max only for raw files
            report_lines.append(f"  - Min Size: {sizeof_fmt(info['min_size'])}")
            report_lines.append(f"  - Max Size: {sizeof_fmt(info['max_size'])}")
    report_lines.append("")

# --- Expansion ratios ---
report_lines.append("## Expansion Ratios\n")
report_lines.append(f"- Chapters PDF → Structured JSON Notes Ratio: {ratio_pdf_to_json:.2f}")
report_lines.append(f"- General Notes PDF → Structured JSON Notes Ratio: {ratio_pdf_to_json_general:.2f}")
report_lines.append(f"- Raw JSON Tables → Structured JSON Tables Ratio: {ratio_json_to_struct:.2f}\n")

# --- Projected Full HTS Storage ---
report_lines.append("## Projected Full HTS Storage\n")
report_lines.append("- **Raw**")
for line in raw_projected:
    report_lines.append(f"  {line}")

report_lines.append("\n- **Structured**")
for line in structured_projected:
    report_lines.append(f"  {line}")

report_lines.append(f"\n- **Total:** {sizeof_fmt(total_bytes)}")

# ---------- Write to Markdown ----------
output_file = "size_report.md"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"Report generated: {output_file}")
