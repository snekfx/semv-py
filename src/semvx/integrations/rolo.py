"""
Rolo integration for semvx - Enhanced table and list formatting.

Provides subprocess-based integration with the Rolo CLI tool for
structured text layout and formatting.
"""

import shutil
import subprocess
from typing import List, Optional


def is_rolo_available() -> bool:
    """Check if rolo command is available."""
    return shutil.which("rolo") is not None


def format_as_table(
    data: List[List[str]],
    headers: Optional[List[str]] = None,
    border: str = "ascii",
    align: Optional[str] = None,
) -> str:
    """
    Format data as a table using rolo.

    Args:
        data: List of rows, each row is a list of cell values
        headers: Optional header row
        border: Border style (none, ascii, unicode)
        align: Column alignment (e.g., "left,right,center")

    Returns:
        Formatted table string
    """
    if not is_rolo_available():
        # Fallback to simple formatting
        return _format_table_fallback(data, headers)

    try:
        # Prepare input data
        rows = []
        if headers:
            rows.append("\t".join(headers))
        for row in data:
            rows.append("\t".join(str(cell) for cell in row))

        input_data = "\n".join(rows)

        # Build rolo command
        cmd = ["rolo", "table", "--delim=\t", f"--border={border}"]
        if align:
            cmd.append(f"--align={align}")

        # Run rolo
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        return _format_table_fallback(data, headers)


def format_as_list(
    items: List[str],
    style: str = "bullets",
    line_numbers: bool = False,
) -> str:
    """
    Format items as a list using rolo.

    Args:
        items: List of items to format
        style: List style (bullets, stars, numbers, dash, dots)
        line_numbers: Whether to add line numbers

    Returns:
        Formatted list string
    """
    if not is_rolo_available():
        # Fallback to simple formatting
        return _format_list_fallback(items, style)

    try:
        input_data = "\n".join(items)

        # Build rolo command
        cmd = ["rolo", "list", f"--list-style={style}"]
        if line_numbers:
            cmd.append("--line-numbers")

        # Run rolo
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        return _format_list_fallback(items, style)


def format_as_columns(
    items: List[str],
    cols: int = 3,
    fill: str = "column",
) -> str:
    """
    Format items as columns using rolo.

    Args:
        items: List of items to format
        cols: Number of columns
        fill: Fill direction (row or column)

    Returns:
        Formatted columns string
    """
    if not is_rolo_available():
        # Fallback to simple formatting
        return _format_columns_fallback(items, cols)

    try:
        input_data = " ".join(items)

        # Build rolo command
        cmd = ["rolo", "columns", f"--cols={cols}", f"--fill={fill}"]

        # Run rolo
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        return _format_columns_fallback(items, cols)


def _format_table_fallback(data: List[List[str]], headers: Optional[List[str]] = None) -> str:
    """Fallback table formatting without rolo."""
    lines = []

    # Calculate column widths
    all_rows = [headers] + data if headers else data
    col_widths = []
    if all_rows:
        num_cols = len(all_rows[0])
        for col_idx in range(num_cols):
            max_width = max(len(str(row[col_idx])) for row in all_rows if col_idx < len(row))
            col_widths.append(max_width)

    # Format rows
    if headers:
        header_line = "  ".join(str(cell).ljust(width) for cell, width in zip(headers, col_widths))
        lines.append(header_line)
        lines.append("-" * len(header_line))

    for row in data:
        row_line = "  ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths))
        lines.append(row_line)

    return "\n".join(lines)


def _format_list_fallback(items: List[str], style: str = "bullets") -> str:
    """Fallback list formatting without rolo."""
    if style == "bullets":
        prefix = "• "
    elif style == "stars":
        prefix = "* "
    elif style == "numbers":
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    elif style == "dash":
        prefix = "- "
    elif style == "dots":
        prefix = "· "
    else:
        prefix = "• "

    return "\n".join(f"{prefix}{item}" for item in items)


def _format_columns_fallback(items: List[str], cols: int = 3) -> str:
    """Fallback column formatting without rolo."""
    lines = []
    for i in range(0, len(items), cols):
        row = items[i : i + cols]
        lines.append("  ".join(row))
    return "\n".join(lines)
