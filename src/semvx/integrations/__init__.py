"""Integrations module for external tools."""

from .boxy import (
    format_status_as_data,
    format_status_for_boxy,
    is_boxy_available,
    render_with_boxy,
    should_use_boxy,
)

__all__ = [
    "is_boxy_available",
    "should_use_boxy",
    "render_with_boxy",
    "format_status_for_boxy",
    "format_status_as_data",
]
