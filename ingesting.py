from src.notes import GeneralNotesSource, SectionNotesSource, ChapterNotesSource, AdditionalUSNotesSource
from src.tables import TariffTableSource
import time
from pathlib import Path

def main():
    """
    Executes a benchmark pipeline for HTS (Harmonized Tariff Schedule) data ingestion.

    The pipeline measures the performance of fetching, parsing, and saving
    various datasets, including general notes, section notes, chapter notes,
    additional U.S. notes, and tariff tables. 

    It produces:
        - Total processing time per dataset
        - Items processed per second
        - Seconds per item
        - Identification of the slowest step (fetch, parse, save)
        - Per-stage timings
        - Per-chapter fetch and parse timings

    Results are written to a Markdown file (`benchmarkIngest.md`) with:
        - Summary table of total times and throughput
        - Table of per-stage timings
        - Per-chapter timings for each dataset
    """
    
    # ----------------- Initialize data source handlers -----------------
    gen_note = GeneralNotesSource()      # General notes
    sec_note = SectionNotesSource()      # Section notes
    ch_note = ChapterNotesSource()       # Chapter notes
    us_note = AdditionalUSNotesSource()  # Additional U.S. notes
    table = TariffTableSource()          # Tariff tables

    # ----------------- Initialize storage containers -----------------
    listGen, listSec, listCh, listUs, listTar = [], [], [], [], []  # Parsed data storage
    benchmarks = []       # Total timing per dataset
    per_stage = []         # Per-stage timing (fetch, parse, save)
    per_item_timings = {} # Per-chapter timings

    # Chapters to process (can expand range for more chapters)
    chapters = range(1, 10)

    def benchmark_dataset(name, source, append_list, chapters, parse_ch=False):
        """
        Benchmarks a single dataset by measuring fetch, parse, and save times.

        Args:
            name (str): Dataset name for reporting.
            source (object): Source handler with `fetch`, `parse`, `save` methods.
            append_list (list): List to store parsed data.
            chapters (iterable): Chapters to process.
            parse_ch (bool): Whether to pass chapter number to parse.

        Side Effects:
            - Appends parsed data to `append_list`.
            - Updates global `benchmarks`, `per-stage`, and `per_item_timings`.
        """
        fetch_time = parse_time = 0.0
        per_item_timings[name] = []  # Initialize per-chapter timing

        for ch in chapters:
            # ---------- Fetch step ----------
            t0 = time.perf_counter()
            path = source.fetch(ch)  # Fetch raw data
            ft = time.perf_counter() - t0
            fetch_time += ft

            # ---------- Parse step ----------
            t0 = time.perf_counter()
            if parse_ch:
                data = source.parse(path, ch)  # Parse with chapter number
            else:
                data = source.parse(path)      # Generic parse
            pt = time.perf_counter() - t0
            parse_time += pt

            if data:
                append_list.append(data)  # Store parsed data

            # Record per-chapter timing
            per_item_timings[name].append((ch, ft, pt))

        # ---------- Save step ----------
        t0 = time.perf_counter()
        source.save(append_list)  # Save entire dataset
        st = time.perf_counter() - t0

        # Record overall timings
        total_time = fetch_time + parse_time + st
        benchmarks.append((name, len(append_list), total_time))
        per_stage.append((name, fetch_time, parse_time, st))

    # ----------------- Run benchmarks for all datasets -----------------
    benchmark_dataset("General Notes", gen_note, listGen, chapters, parse_ch=True)
    benchmark_dataset("Section Notes", sec_note, listSec, chapters)
    benchmark_dataset("Chapter Notes", ch_note, listCh, chapters)
    benchmark_dataset("Additional U.S. Notes", us_note, listUs, chapters)
    benchmark_dataset("Tariff Tables", table, listTar, chapters)

    # ----------------- Write Markdown report -----------------
    md_path = Path("benchmarkIngest.md")
    lines = [
        "# Benchmarks – HTS Ingestion\n\n",
        "This file records how long the ingestion process takes on the available hardware.\n\n",
        "## Summary (Total per dataset)\n\n",
        "| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |\n",
        "|----------------------|---------|----------------|-----------|----------|--------------|\n",
    ]

    # Compute summary metrics for each dataset
    for i, (name, count, total_time) in enumerate(benchmarks):
        items_per_sec = count / total_time if total_time else 0
        sec_per_item = total_time / count if count else 0
        ft, pt, st = per_stage[i][1:]  # Extract per-stage times
        step_times = {'fetch': ft, 'parse': pt, 'save': st}
        slowest_step = max(step_times, key=step_times.get)
        lines.append(
            f"| {name:<20} | {count:5d} | {total_time:10.2f} | {items_per_sec:9.2f} | {sec_per_item:9.2f} | {slowest_step:<12} |\n"
        )

    # ----------------- Detailed per-stage timing table -----------------
    lines.append("\n## Per-stage timings\n\n")
    lines.append("| Dataset              | Fetch(s) | Parse(s) | Save(s) |\n")
    lines.append("|----------------------|----------|----------|---------|\n")
    for name, ft, pt, st in per_stage:
        lines.append(f"| {name:<20} | {ft:8.2f} | {pt:8.2f} | {st:7.2f} |\n")

    # ----------------- Per-chapter timings -----------------
    lines.append("\n## Per-chapter timings\n\n")
    for dataset, items in per_item_timings.items():
        lines.append(f"### {dataset}\n\n")
        lines.append("| Chapter | Fetch(s) | Parse(s) |\n")
        lines.append("|---------|----------|----------|\n")
        for ch, ft, pt in items:
            lines.append(f"| {ch:7d} | {ft:8.2f} | {pt:8.2f} |\n")
        lines.append("\n")

    # Write the complete report to disk
    md_path.write_text("".join(lines), encoding="utf-8")

if __name__ == "__main__":
    main()
