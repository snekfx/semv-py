"""
Boxy integration for semvx - Enhanced visual output.

Provides subprocess-based integration with the Boxy CLI tool for
professional box-drawing and themed output.
"""

import os
import shutil
import subprocess
from typing import Optional


def is_boxy_available() -> bool:
    """Check if boxy command is available."""
    return shutil.which("boxy") is not None


def should_use_boxy() -> bool:
    """
    Determine if boxy should be used based on environment.

    Checks:
    1. SEMVX_USE_BOXY environment variable
    2. Boxy availability
    3. Not in data view mode
    """
    # Check environment variable
    use_boxy = os.environ.get("SEMVX_USE_BOXY", "true").lower()
    if use_boxy in ["false", "0", "no"]:
        return False

    # Check if boxy is available
    if not is_boxy_available():
        return False

    # Check if in data view mode
    view_mode = os.environ.get("SEMVX_VIEW", "normal")
    if view_mode == "data":
        return False

    return True


def render_with_boxy(
    content: str,
    theme: str = "info",
    title: Optional[str] = None,
    style: str = "normal",
    width: Optional[int] = None
) -> str:
    """
    Render content with boxy.

    Args:
        content: Text content to render
        theme: Boxy theme (info, success, warning, error)
        title: Optional title for the box
        style: Border style (normal, rounded, double, heavy, ascii)
        width: Optional fixed width

    Returns:
        Boxed content, or original content if boxy fails
    """
    if not should_use_boxy():
        return content

    try:
        cmd = ["boxy", "--theme", theme, "--style", style]

        if title:
            cmd.extend(["--title", title])

        if width:
            cmd.extend(["--width", str(width)])

        result = subprocess.run(
            cmd,
            input=content,
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to original content
        return content


def format_status_for_boxy(status_data: dict) -> str:
    """
    Format repository status data for boxy display.

    Args:
        status_data: Dictionary with status information

    Returns:
        Formatted string ready for boxy
    """
    lines = []

    # Header
    lines.append("ℹ️  📊 Repository Status")
    lines.append("")

    # User and repo info
    if "user" in status_data:
        lines.append(f"👷 USER: [{status_data['user']}]")

    if "repo_name" in status_data:
        repo_line = f"📦 REPO: [{status_data['repo_name']}]"
        if "current_branch" in status_data:
            repo_line += f" [{status_data['current_branch']}]"
        if "main_branch" in status_data:
            repo_line += f" [{status_data['main_branch']}]"
        lines.append(repo_line)

    # Changes
    if "changed_files" in status_data:
        lines.append(f"✏️  CHNG: [{status_data['changed_files']} file(s)]")

    # Build info
    if "local_build" in status_data or "remote_build" in status_data:
        local = status_data.get("local_build", "?")
        remote = status_data.get("remote_build", "?")
        lines.append(f"🔧 BULD: [local={local} remote={remote}]")

    # Last commit
    if "days_since_last" in status_data:
        days = status_data["days_since_last"]
        msg = status_data.get("last_commit_msg", "unknown")
        if len(msg) > 30:
            msg = msg[:27] + "..."
        lines.append(f"⏱️  LAST: [{days} days] {msg}")

    # Tags
    if "last_tag" in status_data or "release_tag" in status_data:
        last = status_data.get("last_tag", "-none-")
        release = status_data.get("release_tag", "-none-")
        lines.append(f"🏷️  TAGS: last [{last}] release [{release}]")

    # Version
    if "current_version" in status_data or "next_version" in status_data:
        current = status_data.get("current_version", "v0.0.0")
        next_ver = status_data.get("next_version", "?")
        lines.append(f"🔎 VERS: [{current} -> {next_ver}]")

    # Pending actions
    if "pending_actions" in status_data and status_data["pending_actions"]:
        lines.append("")
        lines.append("─── Pending Actions ───")
        for action in status_data["pending_actions"]:
            if len(action) > 50:
                action = action[:47] + "..."
            lines.append(f"+ {action}")

    return "\n".join(lines)


def format_status_as_data(status_data: dict) -> str:
    """
    Format repository status as machine-readable data.

    For AI agents and tool integration (--view=data mode).

    Args:
        status_data: Dictionary with status information

    Returns:
        JSON-like formatted string
    """
    import json
    return json.dumps(status_data, indent=2)
