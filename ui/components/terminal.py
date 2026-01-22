"""Xterm.js terminal component for Nicegui with sidebar, tabs, and split panes."""

from nicegui import ui


class Terminal:
    """Xterm.js terminal component with sidebar, tabs, split panes, and shortcuts."""

    def __init__(self, socket_url: str = ""):
        self.socket_url = socket_url

    def render(self):
        """Render the terminal component."""
        ui.add_head_html('''
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css" />
            <style>
                * { box-sizing: border-box; }

                /* Force nicegui wrapper divs to be full size */
                .nicegui-content > div {
                    width: 100% !important;
                    height: 100% !important;
                }

                .terminal-container {
                    display: flex;
                    flex-direction: row;
                    align-items: stretch;
                    width: 100%;
                    height: 100vh;
                    background: #1e1e1e;
                    overflow: hidden;
                }

                /* Left Sidebar */
                .sidebar {
                    width: 280px;
                    min-width: 280px;
                    background: #252526;
                    border-right: 1px solid #3c3c3c;
                    display: flex;
                    flex-direction: column;
                    transition: width 0.2s, min-width 0.2s;
                    overflow: hidden;
                }
                .sidebar.collapsed {
                    width: 40px;
                    min-width: 40px;
                }
                .sidebar-header {
                    display: flex;
                    align-items: center;
                    padding: 12px;
                    border-bottom: 1px solid #3c3c3c;
                    background: #2d2d2d;
                }
                .sidebar-header h3 {
                    flex: 1;
                    margin: 0;
                    font-size: 14px;
                    font-weight: 600;
                    color: #ccc;
                    white-space: nowrap;
                    overflow: hidden;
                }
                .sidebar.collapsed .sidebar-header h3,
                .sidebar.collapsed .session-list,
                .sidebar.collapsed .workspace-select { display: none; }
                .toggle-btn {
                    background: none;
                    border: none;
                    color: #888;
                    cursor: pointer;
                    padding: 4px 8px;
                    font-size: 14px;
                }
                .toggle-btn:hover { color: #fff; }

                .workspace-select {
                    padding: 12px;
                    border-bottom: 1px solid #3c3c3c;
                    position: relative;
                }
                .workspace-input {
                    width: 100%;
                    padding: 10px 12px;
                    background: #3c3c3c;
                    border: 1px solid #555;
                    border-radius: 6px;
                    color: #fff;
                    font-size: 14px;
                    outline: none;
                }
                .workspace-input:focus { border-color: #007acc; }
                .workspace-input::placeholder { color: #888; }
                .workspace-dropdown {
                    position: absolute;
                    top: 100%;
                    left: 8px;
                    right: 8px;
                    max-height: 300px;
                    overflow-y: auto;
                    background: #2d2d2d;
                    border: 1px solid #555;
                    border-radius: 4px;
                    z-index: 1000;
                    display: none;
                }
                .workspace-dropdown.show { display: block; }
                .workspace-item {
                    padding: 12px 14px;
                    cursor: pointer;
                    font-size: 14px;
                    color: #ccc;
                    border-bottom: 1px solid #3c3c3c;
                }
                .workspace-item:last-child { border-bottom: none; }
                .workspace-item:hover, .workspace-item.selected {
                    background: #094771;
                    color: #fff;
                }
                .workspace-item .git-badge {
                    display: inline-block;
                    background: #3c3c3c;
                    color: #f78166;
                    font-size: 9px;
                    padding: 1px 4px;
                    border-radius: 3px;
                    margin-left: 6px;
                }

                .session-list {
                    flex: 1;
                    overflow-y: auto;
                    padding: 4px 0;
                }
                .session-item {
                    display: flex;
                    align-items: center;
                    padding: 10px 14px;
                    cursor: pointer;
                    color: #aaa;
                    font-size: 14px;
                    border-left: 3px solid transparent;
                }
                .session-item:hover { background: #2d2d2d; }
                .session-item.active {
                    background: #37373d;
                    color: #fff;
                    border-left-color: #007acc;
                }
                .session-item .icon { margin-right: 8px; opacity: 0.7; }
                .session-item .name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
                .session-item .close {
                    opacity: 0;
                    padding: 2px 6px;
                    border-radius: 3px;
                }
                .session-item:hover .close { opacity: 0.5; }
                .session-item .close:hover { opacity: 1; background: rgba(255,255,255,0.1); }

                /* Main Terminal Area */
                .terminal-main {
                    flex: 1 1 auto;
                    display: flex;
                    flex-direction: row;
                    min-width: 0;
                    min-height: 0;
                    position: relative;
                    overflow: hidden;
                }
                .terminal-main > .terminal-pane,
                .terminal-main > .split-container {
                    flex: 1 1 auto;
                    width: 100%;
                    height: 100%;
                }

                .split-container {
                    display: flex;
                    flex: 1;
                    min-width: 0;
                    min-height: 0;
                    overflow: hidden;
                }
                .split-container.vertical { flex-direction: row; }
                .split-container.horizontal { flex-direction: column; }

                .split-handle {
                    flex-shrink: 0;
                    background: #3c3c3c;
                    transition: background 0.15s;
                }
                .split-handle:hover, .split-handle.dragging { background: #007acc; }
                .split-container.vertical > .split-handle { width: 4px; cursor: col-resize; }
                .split-container.horizontal > .split-handle { height: 4px; cursor: row-resize; }

                .terminal-pane {
                    display: flex;
                    flex-direction: column;
                    flex: 1;
                    min-width: 100px;
                    min-height: 80px;
                    background: #1e1e1e;
                    overflow: hidden;
                }
                .terminal-pane.focused > .pane-header { border-bottom-color: #007acc; }

                .pane-header {
                    display: flex;
                    background: #252526;
                    border-bottom: 2px solid #3c3c3c;
                    min-height: 36px;
                    overflow-x: auto;
                }
                .pane-header::-webkit-scrollbar { height: 2px; }

                .pane-tab {
                    display: flex;
                    align-items: center;
                    padding: 8px 12px;
                    background: #2d2d2d;
                    border-right: 1px solid #3c3c3c;
                    cursor: pointer;
                    color: #888;
                    font-size: 13px;
                    width: 180px;
                    min-width: 180px;
                    max-width: 180px;
                }
                .pane-tab:hover { background: #383838; }
                .pane-tab.active { background: #1e1e1e; color: #fff; }
                .pane-tab .name {
                    flex: 1;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                .pane-tab .close {
                    margin-left: 8px;
                    opacity: 0.5;
                    font-size: 16px;
                    padding: 4px 6px;
                    border-radius: 4px;
                    line-height: 1;
                }
                .pane-tab .close:hover {
                    opacity: 1;
                    background: rgba(255, 255, 255, 0.1);
                }

                .pane-content {
                    flex: 1;
                    position: relative;
                    overflow: hidden;
                    min-height: 0;
                }
                .term-container {
                    position: absolute;
                    top: 0; left: 0; right: 0; bottom: 0;
                    display: none;
                }
                .term-container.active { display: block; }

                .drop-indicator {
                    position: absolute;
                    background: rgba(0, 122, 204, 0.3);
                    border: 2px dashed #007acc;
                    pointer-events: none;
                    display: none;
                    z-index: 100;
                }

                .shortcut-help {
                    position: fixed;
                    bottom: 8px;
                    right: 8px;
                    background: rgba(0,0,0,0.85);
                    color: #666;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 9px;
                    z-index: 1000;
                }
                .shortcut-help kbd {
                    background: #333;
                    padding: 1px 3px;
                    border-radius: 2px;
                    margin: 0 1px;
                    font-size: 8px;
                }

                .notification {
                    position: fixed;
                    top: 60px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0,0,0,0.9);
                    color: #fff;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 13px;
                    z-index: 9999;
                    border: 1px solid #007acc;
                }

                .empty-state {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    color: #666;
                    font-size: 14px;
                }
                .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
            </style>
        ''')

        ui.html('''
            <div class="terminal-container" id="terminal-container">
                <div class="sidebar" id="sidebar">
                    <div class="sidebar-header">
                        <h3>Sessions</h3>
                        <button class="toggle-btn" onclick="CT.toggleSidebar()">◀</button>
                    </div>
                    <div class="workspace-select">
                        <input type="text" class="workspace-input" id="workspace-input"
                               placeholder="🔍 Search workspace..."
                               onfocus="CT.showWorkspaceDropdown()"
                               oninput="CT.filterWorkspaces(this.value)"
                               onkeydown="CT.handleWorkspaceKeydown(event)">
                        <div class="workspace-dropdown" id="workspace-dropdown"></div>
                    </div>
                    <div class="session-list" id="session-list"></div>
                </div>
                <div class="terminal-main" id="terminal-main">
                    <div class="empty-state" id="empty-state">
                        <div class="icon">📺</div>
                        <div>Select a workspace to start</div>
                    </div>
                </div>
            </div>
            <div class="shortcut-help">
                <kbd>⌃⇧F</kbd> Focus
                <kbd>⌘D</kbd> Split
                <kbd>⌘W</kbd> Close
                <kbd>⌘⌥↑↓←→</kbd> Navigate
            </div>
        ''', sanitize=False)

        ui.add_body_html('''
            <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.min.js"></script>
            <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
        ''')

        ui.add_body_html(f'''
            <script>
            (function() {{
                const CT = window.claudeTerminal = window.CT = {{
                    socket: null,
                    tabs: {{}},
                    panes: {{}},
                    activeTab: null,
                    focusedPaneId: null,
                    idCounter: 0,
                    dragData: null,
                    focusMode: false,
                    workspaces: [],
                    filteredWorkspaces: [],
                    selectedWorkspaceIndex: -1,
                    manuallyResized: new Set(),

                    init: function() {{
                        this.socket = io('{self.socket_url}', {{ transports: ['websocket', 'polling'] }});
                        this.setupSocketEvents();
                        this.setupKeyboardShortcuts();
                        this.setupBellSound();
                        this.loadWorkspaces();
                        window.addEventListener('resize', () => this.fitAll());
                        // Initial fit after DOM is ready
                        setTimeout(() => this.fitAll(), 100);
                        setTimeout(() => this.fitAll(), 500);
                    }},

                    setupBellSound: function() {{
                        // Create audio context for bell sound
                        this.bellEnabled = true;
                        this.audioContext = null;

                        // Initialize audio context on first user interaction
                        const initAudio = () => {{
                            if (!this.audioContext) {{
                                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                            }}
                            document.removeEventListener('click', initAudio);
                            document.removeEventListener('keydown', initAudio);
                        }};
                        document.addEventListener('click', initAudio);
                        document.addEventListener('keydown', initAudio);
                    }},

                    playBell: function() {{
                        if (!this.bellEnabled || !this.audioContext) return;

                        try {{
                            const oscillator = this.audioContext.createOscillator();
                            const gainNode = this.audioContext.createGain();

                            oscillator.connect(gainNode);
                            gainNode.connect(this.audioContext.destination);

                            oscillator.frequency.value = 800;
                            oscillator.type = 'sine';

                            gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
                            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);

                            oscillator.start(this.audioContext.currentTime);
                            oscillator.stop(this.audioContext.currentTime + 0.1);
                        }} catch (e) {{
                            console.log('Bell sound error:', e);
                        }}
                    }},

                    loadWorkspaces: function() {{
                        // Load from backend via page reload workaround - workspaces are embedded
                        fetch('/api/workspaces').then(r => r.json()).then(data => {{
                            this.workspaces = data;
                            this.renderWorkspaceSelect();
                        }}).catch(() => {{
                            // Fallback: parse from existing nicegui select if available
                            const ngSelect = document.querySelector('.q-select');
                            if (ngSelect) {{
                                // Will be populated by nicegui
                            }}
                        }});
                    }},

                    renderWorkspaceSelect: function() {{
                        // Initial render of dropdown
                        this.filterWorkspaces('');
                    }},

                    showWorkspaceDropdown: function() {{
                        const dropdown = document.getElementById('workspace-dropdown');
                        dropdown.classList.add('show');
                        this.selectedWorkspaceIndex = -1;
                        this.filterWorkspaces(document.getElementById('workspace-input').value);

                        // Close on outside click
                        const closeHandler = (e) => {{
                            if (!e.target.closest('.workspace-select')) {{
                                dropdown.classList.remove('show');
                                document.removeEventListener('click', closeHandler);
                            }}
                        }};
                        setTimeout(() => document.addEventListener('click', closeHandler), 0);
                    }},

                    filterWorkspaces: function(query) {{
                        const dropdown = document.getElementById('workspace-dropdown');
                        const q = query.toLowerCase().trim();

                        const filtered = this.workspaces.filter(ws =>
                            ws.name.toLowerCase().includes(q) ||
                            ws.path.toLowerCase().includes(q)
                        );

                        dropdown.innerHTML = filtered.map((ws, idx) => `
                            <div class="workspace-item" data-path="${{ws.path}}" data-index="${{idx}}"
                                 onclick="CT.selectWorkspace('${{ws.path.replace(/'/g, "\\'")}}')">
                                ${{ws.name}}${{ws.is_git ? '<span class="git-badge">git</span>' : ''}}
                            </div>
                        `).join('');

                        this.filteredWorkspaces = filtered;
                        this.selectedWorkspaceIndex = filtered.length > 0 ? 0 : -1;
                        this.updateWorkspaceSelection();
                    }},

                    handleWorkspaceKeydown: function(e) {{
                        const dropdown = document.getElementById('workspace-dropdown');
                        if (!dropdown.classList.contains('show')) {{
                            if (e.key === 'ArrowDown' || e.key === 'Enter') {{
                                this.showWorkspaceDropdown();
                                e.preventDefault();
                            }}
                            return;
                        }}

                        if (e.key === 'ArrowDown') {{
                            e.preventDefault();
                            if (this.selectedWorkspaceIndex < this.filteredWorkspaces.length - 1) {{
                                this.selectedWorkspaceIndex++;
                                this.updateWorkspaceSelection();
                            }}
                        }} else if (e.key === 'ArrowUp') {{
                            e.preventDefault();
                            if (this.selectedWorkspaceIndex > 0) {{
                                this.selectedWorkspaceIndex--;
                                this.updateWorkspaceSelection();
                            }}
                        }} else if (e.key === 'Enter') {{
                            e.preventDefault();
                            if (this.selectedWorkspaceIndex >= 0 && this.filteredWorkspaces[this.selectedWorkspaceIndex]) {{
                                this.selectWorkspace(this.filteredWorkspaces[this.selectedWorkspaceIndex].path);
                            }}
                        }} else if (e.key === 'Escape') {{
                            dropdown.classList.remove('show');
                        }}
                    }},

                    updateWorkspaceSelection: function() {{
                        const items = document.querySelectorAll('.workspace-item');
                        items.forEach((item, idx) => {{
                            item.classList.toggle('selected', idx === this.selectedWorkspaceIndex);
                        }});
                        // Scroll into view
                        const selected = items[this.selectedWorkspaceIndex];
                        if (selected) selected.scrollIntoView({{ block: 'nearest' }});
                    }},

                    selectWorkspace: function(path) {{
                        const dropdown = document.getElementById('workspace-dropdown');
                        const input = document.getElementById('workspace-input');
                        dropdown.classList.remove('show');
                        input.value = '';
                        input.blur();
                        this.createSession(path);
                    }},

                    toggleSidebar: function() {{
                        const sidebar = document.getElementById('sidebar');
                        const btn = sidebar.querySelector('.toggle-btn');
                        sidebar.classList.toggle('collapsed');
                        btn.textContent = sidebar.classList.contains('collapsed') ? '▶' : '◀';
                        setTimeout(() => this.fitAll(), 250);
                    }},

                    setupSocketEvents: function() {{
                        this.socket.on('connect', () => console.log('Socket connected'));

                        this.socket.on('session_started', (data) => {{
                            const tab = this.tabs[data.tab_id];
                            if (tab) {{
                                tab.connected = true;
                                tab.term.focus();

                                // Multiple resize attempts to ensure correct dimensions
                                const doResize = () => {{
                                    tab.fitAddon.fit();
                                    this.socket.emit('terminal_resize', {{
                                        tab_id: data.tab_id,
                                        cols: tab.term.cols,
                                        rows: tab.term.rows
                                    }});
                                }};

                                doResize();
                                setTimeout(doResize, 100);
                                setTimeout(doResize, 300);
                                setTimeout(doResize, 500);
                            }}
                        }});

                        this.socket.on('terminal_output', (data) => {{
                            const tab = this.tabs[data.tab_id];
                            if (!tab) return;
                            if (!tab.started) {{
                                tab.buffer += data.data;
                                if (tab.buffer.includes('Claude Code') || tab.buffer.includes('claude>')) {{
                                    tab.started = true;
                                    tab.term.clear();
                                    const idx = tab.buffer.indexOf('Claude Code');
                                    tab.term.write(idx >= 0 ? tab.buffer.substring(idx) : tab.buffer);
                                    tab.buffer = '';
                                }}
                            }} else {{
                                tab.term.write(data.data);
                            }}
                        }});

                        this.socket.on('terminal_error', (data) => {{
                            const tab = this.tabs[data.tab_id];
                            if (tab) tab.term.write('\\r\\n[Error] ' + data.message + '\\r\\n');
                        }});

                        this.socket.on('session_closed', (data) => {{
                            const tab = this.tabs[data.tab_id];
                            // Only close if tab exists and not already closing
                            if (tab && !tab.closing) {{
                                this.closeTab(data.tab_id);
                            }}
                        }});
                    }},

                    setupKeyboardShortcuts: function() {{
                        document.addEventListener('keydown', (e) => {{
                            const mod = navigator.platform.includes('Mac') ? e.metaKey : e.ctrlKey;
                            if (!mod) return;

                            if (e.key === 'd' && !e.shiftKey && !e.altKey) {{
                                e.preventDefault();
                                this.splitCurrentPane('vertical');
                            }} else if (e.key === 'D' || (e.key === 'd' && e.shiftKey)) {{
                                e.preventDefault();
                                this.splitCurrentPane('horizontal');
                            }} else if (e.key === 'w' && !e.shiftKey) {{
                                e.preventDefault();
                                if (this.activeTab) this.closeTab(this.activeTab);
                            }} else if (e.altKey && ['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)) {{
                                e.preventDefault();
                                this.navigatePane(e.key.replace('Arrow','').toLowerCase());
                            }}
                        }});
                    }},

                    createSession: function(workspace) {{
                        document.getElementById('empty-state')?.remove();

                        // Create pane if none exists
                        if (Object.keys(this.panes).length === 0) {{
                            const main = document.getElementById('terminal-main');
                            this.createPane(main, 'root');
                            this.focusedPaneId = 'root';
                        }}

                        const paneId = this.focusedPaneId || Object.keys(this.panes)[0];
                        this.createTab(workspace, paneId);
                    }},

                    createPane: function(container, id) {{
                        const paneId = id || 'pane_' + (++this.idCounter);

                        const pane = document.createElement('div');
                        pane.className = 'terminal-pane';
                        pane.id = paneId;

                        const header = document.createElement('div');
                        header.className = 'pane-header';

                        const content = document.createElement('div');
                        content.className = 'pane-content';

                        // Click on content to focus pane
                        content.addEventListener('mousedown', () => this.focusPane(paneId));

                        const dropIndicator = document.createElement('div');
                        dropIndicator.className = 'drop-indicator';
                        content.appendChild(dropIndicator);

                        pane.appendChild(header);
                        pane.appendChild(content);
                        container.appendChild(pane);

                        this.setupPaneDragDrop(pane, content, dropIndicator);

                        this.panes[paneId] = {{
                            element: pane,
                            header: header,
                            content: content,
                            tabIds: [],
                            dropIndicator: dropIndicator
                        }};

                        return paneId;
                    }},

                    focusPane: function(paneId) {{
                        const pane = this.panes[paneId];
                        if (!pane) return;

                        // Update visual focus
                        Object.values(this.panes).forEach(p => p.element.classList.remove('focused'));
                        pane.element.classList.add('focused');

                        this.focusedPaneId = paneId;

                        // Switch to active tab in this pane if any
                        if (pane.tabIds.length > 0) {{
                            const currentActiveInPane = pane.tabIds.find(tid => {{
                                const tabEl = document.getElementById('tab-btn-' + tid);
                                return tabEl && tabEl.classList.contains('active');
                            }});
                            const tabToFocus = currentActiveInPane || pane.tabIds[0];
                            this.switchTab(tabToFocus);
                        }}
                    }},

                    setupPaneDragDrop: function(pane, content, indicator) {{
                        content.addEventListener('dragover', (e) => {{
                            if (!this.dragData) return;
                            e.preventDefault();
                            const rect = content.getBoundingClientRect();
                            const x = (e.clientX - rect.left) / rect.width;
                            const y = (e.clientY - rect.top) / rect.height;
                            let zone = 'center';
                            if (x < 0.25) zone = 'left';
                            else if (x > 0.75) zone = 'right';
                            else if (y < 0.25) zone = 'top';
                            else if (y > 0.75) zone = 'bottom';

                            const styles = {{
                                left: 'left:0;top:0;width:50%;height:100%',
                                right: 'right:0;top:0;width:50%;height:100%',
                                top: 'left:0;top:0;width:100%;height:50%',
                                bottom: 'left:0;bottom:0;width:100%;height:50%',
                                center: 'left:10%;top:10%;width:80%;height:80%'
                            }};
                            indicator.style.cssText = 'display:block;' + styles[zone];
                            this.dragData.dropZone = zone;
                            this.dragData.targetPane = pane.id;
                        }});

                        content.addEventListener('dragleave', (e) => {{
                            if (!content.contains(e.relatedTarget)) indicator.style.display = 'none';
                        }});

                        content.addEventListener('drop', (e) => {{
                            e.preventDefault();
                            indicator.style.display = 'none';
                            if (!this.dragData) return;
                            const {{ tabId, dropZone, targetPane }} = this.dragData;
                            this.handleTabDrop(tabId, targetPane, dropZone);
                            this.dragData = null;
                        }});
                    }},

                    handleTabDrop: function(tabId, targetPaneId, zone) {{
                        const tab = this.tabs[tabId];
                        if (!tab) return;
                        if (zone === 'center') {{
                            if (tab.paneId !== targetPaneId) this.moveTabToPane(tabId, targetPaneId);
                        }} else {{
                            const direction = (zone === 'left' || zone === 'right') ? 'vertical' : 'horizontal';
                            const newPaneId = this.splitPaneAt(targetPaneId, direction, zone === 'right' || zone === 'bottom');
                            this.moveTabToPane(tabId, newPaneId);
                        }}
                    }},

                    moveTabToPane: function(tabId, newPaneId) {{
                        const tab = this.tabs[tabId];
                        if (!tab || tab.paneId === newPaneId) return;

                        const oldPane = this.panes[tab.paneId];
                        const newPane = this.panes[newPaneId];

                        oldPane.tabIds = oldPane.tabIds.filter(id => id !== tabId);

                        const tabBtn = document.getElementById('tab-btn-' + tabId);
                        newPane.header.appendChild(tabBtn);
                        newPane.content.appendChild(tab.termContainer);
                        newPane.tabIds.push(tabId);
                        tab.paneId = newPaneId;

                        this.cleanupEmptyPane(oldPane.element.id);
                        this.switchTab(tabId);
                        setTimeout(() => this.fitAll(), 50);
                    }},

                    createTab: function(workspace, paneId) {{
                        const tabId = 'tab_' + (++this.idCounter);
                        const pane = this.panes[paneId];
                        if (!pane) return null;

                        const workspaceName = workspace.split('/').pop();

                        // Tab button
                        const tabBtn = document.createElement('div');
                        tabBtn.className = 'pane-tab';
                        tabBtn.id = 'tab-btn-' + tabId;
                        tabBtn.draggable = true;
                        tabBtn.innerHTML = `<span class="name">${{workspaceName}}</span><span class="close">×</span>`;
                        tabBtn.querySelector('.name').onclick = () => this.switchTab(tabId);
                        tabBtn.querySelector('.close').onclick = (e) => {{ e.stopPropagation(); this.closeTab(tabId); }};
                        tabBtn.addEventListener('dragstart', () => {{ this.dragData = {{ tabId }}; tabBtn.style.opacity = '0.5'; }});
                        tabBtn.addEventListener('dragend', () => {{
                            tabBtn.style.opacity = '1';
                            this.dragData = null;
                            document.querySelectorAll('.drop-indicator').forEach(el => el.style.display = 'none');
                        }});
                        pane.header.appendChild(tabBtn);

                        // Terminal container
                        const termContainer = document.createElement('div');
                        termContainer.className = 'term-container';
                        termContainer.id = 'term-' + tabId;
                        pane.content.appendChild(termContainer);

                        // xterm
                        const term = new Terminal({{
                            cursorBlink: true,
                            fontSize: 12,
                            fontFamily: '"Cascadia Code", Menlo, Monaco, monospace',
                            theme: {{ background: '#1e1e1e', foreground: '#d4d4d4', cursor: '#d4d4d4', selectionBackground: '#264f78' }},
                            scrollback: 10000,
                            bellStyle: 'sound'
                        }});

                        // Bell sound handler
                        term.onBell(() => this.playBell());

                        const fitAddon = new FitAddon.FitAddon();
                        term.loadAddon(fitAddon);
                        term.open(termContainer);

                        // Key handling
                        term.attachCustomKeyEventHandler((e) => {{
                            if (e.type !== 'keydown') return true;
                            const send = (data) => {{ if (this.tabs[tabId]?.connected) this.socket.emit('terminal_input', {{ tab_id: tabId, data }}); }};

                            // Toggle focus mode: Ctrl+Shift+F
                            if (e.key === 'F' && e.ctrlKey && e.shiftKey) {{
                                this.focusMode = !this.focusMode;
                                this.notify(this.focusMode ? '🔒 Focus Mode ON' : '🔓 Focus Mode OFF');
                                return false;
                            }}

                            if (this.focusMode) {{
                                e.preventDefault();
                                e.stopPropagation();
                                if (e.key === 'Tab') send(e.shiftKey ? '\\x1b[Z' : '\\t');
                                else if (e.key === 'Enter') send(e.shiftKey ? '\\x1b[13;2u' : e.altKey ? '\\x1b[13;3u' : '\\r');
                                else if (e.key === 'Escape') send('\\x1b');
                                else if (e.key === 'Backspace') send('\\x7f');
                                else if (e.key.startsWith('Arrow')) send({{ArrowUp:'\\x1b[A',ArrowDown:'\\x1b[B',ArrowRight:'\\x1b[C',ArrowLeft:'\\x1b[D'}}[e.key]);
                                else if (e.ctrlKey && e.key.length === 1) {{ const c = e.key.toUpperCase().charCodeAt(0) - 64; if (c > 0 && c < 32) send(String.fromCharCode(c)); }}
                                else if (e.altKey && e.key.length === 1) send('\\x1b' + e.key);
                                else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) send(e.key);
                                return false;
                            }}

                            // Normal mode: Shift+Enter only
                            if (e.key === 'Enter' && e.shiftKey && !e.ctrlKey && !e.metaKey && !e.altKey) {{
                                e.preventDefault();
                                send('\\x1b[13;2u');
                                return false;
                            }}
                            return true;
                        }});

                        // Auto-copy on selection
                        term.onSelectionChange(() => {{
                            const sel = term.getSelection();
                            if (sel) navigator.clipboard.writeText(sel).catch(() => {{}});
                        }});

                        term.onData((data) => {{
                            if (this.tabs[tabId]?.connected) this.socket.emit('terminal_input', {{ tab_id: tabId, data }});
                        }});

                        // Store tab data first
                        const tabData = {{
                            term, fitAddon, workspace, paneId,
                            termContainer, connected: false, started: false, buffer: '',
                            resizeObserver: null
                        }};
                        this.tabs[tabId] = tabData;
                        pane.tabIds.push(tabId);

                        // Use ResizeObserver for reliable fit
                        const resizeObserver = new ResizeObserver(() => {{
                            const t = this.tabs[tabId];
                            if (!t) return;
                            t.fitAddon.fit();
                            if (t.connected) {{
                                this.socket.emit('terminal_resize', {{
                                    tab_id: tabId,
                                    cols: t.term.cols,
                                    rows: t.term.rows
                                }});
                            }}
                        }});
                        resizeObserver.observe(termContainer);
                        tabData.resizeObserver = resizeObserver;

                        this.switchTab(tabId);
                        this.focusPane(paneId);
                        this.updateSessionList();

                        // Fit first, then start session with correct dimensions
                        fitAddon.fit();

                        // Delay session start to ensure container is fully rendered
                        setTimeout(() => {{
                            fitAddon.fit();
                            this.socket.emit('start_session', {{
                                tab_id: tabId,
                                workspace: workspace,
                                cols: term.cols,
                                rows: term.rows
                            }});
                        }}, 100);

                        return tabId;
                    }},

                    switchTab: function(tabId) {{
                        const tab = this.tabs[tabId];
                        if (!tab) return;

                        const pane = this.panes[tab.paneId];
                        pane.tabIds.forEach(tid => {{
                            const t = this.tabs[tid];
                            if (t) {{
                                t.termContainer.classList.remove('active');
                                document.getElementById('tab-btn-' + tid)?.classList.remove('active');
                            }}
                        }});

                        tab.termContainer.classList.add('active');
                        document.getElementById('tab-btn-' + tabId)?.classList.add('active');

                        this.activeTab = tabId;
                        this.focusedPaneId = tab.paneId;

                        Object.values(this.panes).forEach(p => p.element.classList.remove('focused'));
                        pane.element.classList.add('focused');

                        tab.fitAddon.fit();
                        tab.term.focus();
                        this.updateSessionList();
                    }},

                    closeTab: function(tabId) {{
                        const tab = this.tabs[tabId];
                        if (!tab || tab.closing) return;

                        // Mark as closing to prevent double-close
                        tab.closing = true;

                        // Notify server if still connected
                        if (tab.connected) {{
                            tab.connected = false;
                            this.socket.emit('stop_session', {{ tab_id: tabId }});
                        }}

                        // Clean up ResizeObserver
                        if (tab.resizeObserver) {{
                            tab.resizeObserver.disconnect();
                        }}

                        const paneId = tab.paneId;
                        const pane = this.panes[paneId];
                        if (pane) {{
                            pane.tabIds = pane.tabIds.filter(id => id !== tabId);
                        }}

                        document.getElementById('tab-btn-' + tabId)?.remove();
                        tab.termContainer?.remove();
                        try {{ tab.term.dispose(); }} catch(e) {{}}
                        delete this.tabs[tabId];

                        if (this.activeTab === tabId) {{
                            if (pane.tabIds.length > 0) {{
                                this.switchTab(pane.tabIds[pane.tabIds.length - 1]);
                            }} else {{
                                const otherPane = Object.values(this.panes).find(p => p.tabIds.length > 0);
                                if (otherPane) this.switchTab(otherPane.tabIds[0]);
                                else this.activeTab = null;
                            }}
                        }}

                        this.cleanupEmptyPane(paneId);
                        this.updateSessionList();
                    }},

                    cleanupEmptyPane: function(paneId) {{
                        const pane = this.panes[paneId];
                        if (!pane || pane.tabIds.length > 0) return;

                        // If this is the last pane, show empty state instead of removing
                        if (Object.keys(this.panes).length <= 1) {{
                            // Remove the pane and show empty state
                            delete this.panes[paneId];
                            pane.element.remove();
                            this.focusedPaneId = null;
                            this.activeTab = null;

                            // Show empty state
                            const main = document.getElementById('terminal-main');
                            if (main && !document.getElementById('empty-state')) {{
                                const emptyState = document.createElement('div');
                                emptyState.className = 'empty-state';
                                emptyState.id = 'empty-state';
                                emptyState.innerHTML = '<div class="icon">📺</div><div>Select a workspace to start</div>';
                                main.appendChild(emptyState);
                            }}
                            return;
                        }}

                        const paneEl = pane.element;
                        const parent = paneEl.parentElement;

                        if (parent.classList.contains('split-container')) {{
                            const children = Array.from(parent.children).filter(el =>
                                el.classList.contains('terminal-pane') || el.classList.contains('split-container')
                            );
                            const sibling = children.find(el => el !== paneEl);

                            if (sibling && parent.parentElement) {{
                                const grandparent = parent.parentElement;
                                grandparent.insertBefore(sibling, parent);
                                parent.remove();
                                sibling.style.flex = '1';
                                sibling.style.width = '';
                                sibling.style.height = '';
                                // Clear manual resize flag for this container
                                this.manuallyResized.delete(parent.id);
                            }}
                        }}

                        delete this.panes[paneId];
                        paneEl.remove();

                        // Update focused pane
                        if (this.focusedPaneId === paneId) {{
                            this.focusedPaneId = Object.keys(this.panes)[0] || null;
                        }}

                        setTimeout(() => this.fitAll(), 50);
                    }},

                    splitCurrentPane: function(direction) {{
                        if (!this.focusedPaneId || !this.panes[this.focusedPaneId]) return;
                        const currentTab = this.activeTab ? this.tabs[this.activeTab] : null;
                        const workspace = currentTab?.workspace;
                        if (!workspace) return;

                        const newPaneId = this.splitPaneAt(this.focusedPaneId, direction, true);
                        this.createTab(workspace, newPaneId);
                    }},

                    splitPaneAt: function(paneId, direction, insertAfter) {{
                        const pane = this.panes[paneId];
                        if (!pane) return paneId;

                        const paneEl = pane.element;
                        const parent = paneEl.parentElement;

                        // Check if parent is already a split-container with same direction
                        if (parent.classList.contains('split-container') && parent.classList.contains(direction)) {{
                            // Add to existing container instead of nesting
                            const handle = document.createElement('div');
                            handle.className = 'split-handle';
                            handle.addEventListener('mousedown', (e) => this.startResize(e, parent, handle));

                            const newPaneId = this.createPane(parent);
                            const newPaneEl = this.panes[newPaneId].element;

                            if (insertAfter) {{
                                // Insert after current pane
                                paneEl.after(handle);
                                handle.after(newPaneEl);
                            }} else {{
                                // Insert before current pane
                                paneEl.before(newPaneEl);
                                newPaneEl.after(handle);
                            }}

                            // Redistribute all children equally
                            this.redistributeSizes(parent);
                            setTimeout(() => this.fitAll(), 50);
                            return newPaneId;
                        }}

                        // Create new split container
                        const splitContainer = document.createElement('div');
                        splitContainer.className = 'split-container ' + direction;
                        splitContainer.id = 'split_' + (++this.idCounter);

                        const handle = document.createElement('div');
                        handle.className = 'split-handle';
                        handle.addEventListener('mousedown', (e) => this.startResize(e, splitContainer, handle));

                        const newPaneId = this.createPane(splitContainer);
                        const newPaneEl = this.panes[newPaneId].element;

                        parent.insertBefore(splitContainer, paneEl);

                        if (insertAfter) {{
                            splitContainer.appendChild(paneEl);
                            splitContainer.appendChild(handle);
                            splitContainer.appendChild(newPaneEl);
                        }} else {{
                            splitContainer.appendChild(newPaneEl);
                            splitContainer.appendChild(handle);
                            splitContainer.appendChild(paneEl);
                        }}

                        // Equal distribution if not manually resized
                        this.redistributeSizes(splitContainer);

                        setTimeout(() => this.fitAll(), 50);
                        return newPaneId;
                    }},

                    redistributeSizes: function(container) {{
                        if (this.manuallyResized.has(container.id)) return;

                        const isVertical = container.classList.contains('vertical');
                        const children = Array.from(container.children).filter(el =>
                            el.classList.contains('terminal-pane') || el.classList.contains('split-container')
                        );

                        children.forEach(child => {{
                            child.style.flex = '1';
                            child.style.width = '';
                            child.style.height = '';
                        }});
                    }},

                    startResize: function(e, container, handle) {{
                        e.preventDefault();
                        handle.classList.add('dragging');

                        // Mark as manually resized
                        this.manuallyResized.add(container.id);

                        const isVertical = container.classList.contains('vertical');
                        const children = Array.from(container.children).filter(el =>
                            el.classList.contains('terminal-pane') || el.classList.contains('split-container')
                        );
                        if (children.length < 2) return;

                        const first = children[0], second = children[1];
                        const startPos = isVertical ? e.clientX : e.clientY;
                        const containerSize = isVertical ? container.offsetWidth : container.offsetHeight;
                        const handleSize = isVertical ? handle.offsetWidth : handle.offsetHeight;
                        const startFirst = isVertical ? first.offsetWidth : first.offsetHeight;

                        const onMove = (e) => {{
                            const delta = (isVertical ? e.clientX : e.clientY) - startPos;
                            const newFirst = Math.max(100, Math.min(containerSize - 100 - handleSize, startFirst + delta));
                            const newSecond = containerSize - newFirst - handleSize;

                            first.style.flex = 'none';
                            second.style.flex = 'none';
                            if (isVertical) {{
                                first.style.width = newFirst + 'px';
                                second.style.width = newSecond + 'px';
                            }} else {{
                                first.style.height = newFirst + 'px';
                                second.style.height = newSecond + 'px';
                            }}
                            this.fitAll();
                        }};

                        const onUp = () => {{
                            handle.classList.remove('dragging');
                            document.removeEventListener('mousemove', onMove);
                            document.removeEventListener('mouseup', onUp);
                        }};

                        document.addEventListener('mousemove', onMove);
                        document.addEventListener('mouseup', onUp);
                    }},

                    navigatePane: function(direction) {{
                        if (!this.focusedPaneId) return;
                        const currentPane = this.panes[this.focusedPaneId];
                        if (!currentPane) return;

                        const currentRect = currentPane.element.getBoundingClientRect();
                        const cx = currentRect.left + currentRect.width / 2;
                        const cy = currentRect.top + currentRect.height / 2;

                        let bestPane = null, bestDist = Infinity;

                        Object.entries(this.panes).forEach(([id, pane]) => {{
                            if (id === this.focusedPaneId || pane.tabIds.length === 0) return;
                            const rect = pane.element.getBoundingClientRect();
                            const px = rect.left + rect.width / 2;
                            const py = rect.top + rect.height / 2;

                            let inDir = false;
                            if (direction === 'left' && px < cx) inDir = true;
                            if (direction === 'right' && px > cx) inDir = true;
                            if (direction === 'up' && py < cy) inDir = true;
                            if (direction === 'down' && py > cy) inDir = true;

                            if (inDir) {{
                                const dist = Math.sqrt(Math.pow(px - cx, 2) + Math.pow(py - cy, 2));
                                if (dist < bestDist) {{ bestDist = dist; bestPane = pane; }}
                            }}
                        }});

                        if (bestPane && bestPane.tabIds.length > 0) {{
                            this.focusPane(bestPane.element.id);
                        }}
                    }},

                    updateSessionList: function() {{
                        const list = document.getElementById('session-list');
                        list.innerHTML = '';

                        Object.entries(this.tabs).forEach(([tabId, tab]) => {{
                            const item = document.createElement('div');
                            item.className = 'session-item' + (tabId === this.activeTab ? ' active' : '');
                            item.innerHTML = `
                                <span class="icon">▸</span>
                                <span class="name">${{tab.workspace.split('/').pop()}}</span>
                                <span class="close" onclick="event.stopPropagation(); CT.closeTab('${{tabId}}')">×</span>
                            `;
                            item.onclick = () => this.switchTab(tabId);
                            list.appendChild(item);
                        }});
                    }},

                    fitAll: function() {{
                        Object.entries(this.tabs).forEach(([tabId, tab]) => {{
                            try {{
                                tab.fitAddon.fit();
                                if (tab.connected) {{
                                    this.socket.emit('terminal_resize', {{
                                        tab_id: tabId,
                                        cols: tab.term.cols,
                                        rows: tab.term.rows
                                    }});
                                }}
                            }} catch(e) {{}}
                        }});
                    }},

                    notify: function(msg) {{
                        document.querySelector('.notification')?.remove();
                        const n = document.createElement('div');
                        n.className = 'notification';
                        n.textContent = msg;
                        document.body.appendChild(n);
                        setTimeout(() => n.remove(), 2000);
                    }}
                }};

                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', () => CT.init());
                }} else {{
                    setTimeout(() => CT.init(), 100);
                }}
            }})();
            </script>
        ''')


def start_session(workspace: str, password: str = None):
    """Start terminal session with workspace."""
    ui.run_javascript(f"window.CT.createSession('{workspace}')")


def stop_session():
    """Stop current terminal session."""
    ui.run_javascript("if (window.CT.activeTab) window.CT.closeTab(window.CT.activeTab)")
