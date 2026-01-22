"""Workspace selector component for Nicegui."""

import os
from pathlib import Path
from typing import Callable, List, Optional

from nicegui import ui


def get_workspaces() -> List[dict]:
    """Get list of available workspaces sorted alphabetically.

    Returns:
        List of workspace info dicts sorted by name (no duplicates)
    """
    home = Path.home()
    seen_paths = set()  # Track paths to avoid duplicates (macOS case-insensitive)
    workspaces = []

    # Common workspace directories - check only one case
    common_dirs = ["Workspace", "Projects", "dev", "code"]

    for dir_name in common_dirs:
        dir_path = home / dir_name
        if dir_path.is_dir():
            # Resolve to real path to handle case-insensitivity
            real_dir = dir_path.resolve()
            if str(real_dir) in seen_paths:
                continue
            seen_paths.add(str(real_dir))

            # Add subdirectories
            try:
                for sub in dir_path.iterdir():
                    if sub.is_dir() and not sub.name.startswith("."):
                        real_sub = sub.resolve()
                        if str(real_sub) in seen_paths:
                            continue
                        seen_paths.add(str(real_sub))

                        display_name = f"{dir_name}/{sub.name}"
                        if (sub / ".git").exists():
                            display_name += " (git)"
                        workspaces.append({
                            "name": display_name,
                            "path": str(sub),
                            "is_git": (sub / ".git").exists(),
                        })
            except PermissionError:
                pass

    # Sort alphabetically by name
    workspaces.sort(key=lambda x: x["name"].lower())

    # Add home directory at the end
    workspaces.append({
        "name": "~ (Home)",
        "path": str(home),
        "is_git": (home / ".git").exists(),
    })

    return workspaces


class WorkspaceSelector:
    """Workspace selector with optional password input."""

    def __init__(self, on_connect: Callable[[str, Optional[str]], None]):
        """Initialize workspace selector.

        Args:
            on_connect: Callback when connect is clicked (workspace, password)
        """
        self.on_connect = on_connect
        self.workspaces = get_workspaces()
        self.selected_workspace: Optional[str] = None
        self.password_input: Optional[ui.input] = None
        self.show_password = False

    def render(self):
        """Render the workspace selector UI."""
        with ui.card().classes("w-full max-w-xl mx-auto p-4"):
            ui.label("Claude Web Terminal").classes("text-2xl font-bold mb-4")

            # Workspace dropdown
            workspace_options = {ws["path"]: ws["name"] for ws in self.workspaces}

            with ui.row().classes("w-full items-center gap-2"):
                ui.label("Workspace:").classes("w-24")
                self.workspace_select = ui.select(
                    options=workspace_options,
                    label="Select workspace",
                    on_change=lambda e: self._on_workspace_change(e.value),
                ).classes("flex-grow")

            # Password input (optional, collapsed by default)
            with ui.expansion("SSH Password (optional)", icon="key").classes("w-full"):
                with ui.row().classes("w-full items-center gap-2"):
                    self.password_input = ui.input(
                        label="Password",
                        password=True,
                        password_toggle_button=True,
                    ).classes("flex-grow")

            # Connect button
            with ui.row().classes("w-full justify-end mt-4"):
                ui.button("Connect", on_click=self._on_connect_click).props("color=primary")

    def render_compact(self):
        """Render compact workspace selector for top bar."""
        workspace_options = {ws["path"]: ws["name"] for ws in self.workspaces}

        self.workspace_select = ui.select(
            options=workspace_options,
            label="Workspace",
            on_change=lambda e: self._on_workspace_change(e.value),
        ).classes("w-64").props("dense dark")

        ui.button("Connect", on_click=self._on_connect_click).props("dense color=primary")

    def _on_workspace_change(self, value: str):
        """Handle workspace selection change."""
        self.selected_workspace = value

    def _on_connect_click(self):
        """Handle connect button click."""
        if self.selected_workspace:
            password = None
            if self.password_input and self.password_input.value:
                password = self.password_input.value
            self.on_connect(self.selected_workspace, password)
        else:
            ui.notify("Please select a workspace", type="warning")
