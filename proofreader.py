import sys
import os
import json
import hashlib
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget,
    QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QSplitter, QFileDialog, QMessageBox, QMenu
)
from PySide6.QtCore import Qt


STATE_FILE = "state.json"

class ProofReaderApp(QMainWindow):

    def _get_node_hash(self, story, node):
        node_path = os.path.join("stories", story, "nodes", f"{node}.txt")
        if os.path.exists(node_path):
            with open(node_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        return None
    def __init__(self):
        super().__init__()
        from PySide6.QtWidgets import QLabel
        self.status_bar = self.statusBar()
        self.status_label_all = QLabel()
        self.status_label_story = QLabel()
        self.status_bar.addWidget(self.status_label_all)
        self.status_bar.addWidget(self.status_label_story)
        self.state = self.load_state()
        self.current_story = None
        self.current_node = None
        self.text_size = 12

        # Restore window geometry/state if available
        winstate = self.state.get("window", {})
        if winstate.get("maximized"):
            self.showMaximized()
        # Layouts
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Left: Tree with control buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Top row: Refresh and Publish
        btn_top_row = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Stories")
        self.publish_btn = QPushButton("Publish Story")
        btn_top_row.addWidget(self.refresh_btn)
        btn_top_row.addWidget(self.publish_btn)
        left_layout.addLayout(btn_top_row)

        # Second row: Expand/Collapse
        btn_row = QHBoxLayout()
        btn_expand = QPushButton("Expand All")
        btn_collapse = QPushButton("Collapse All")
        btn_row.addWidget(btn_expand)
        btn_row.addWidget(btn_collapse)
        left_layout.addLayout(btn_row)

        # Third row: Accept/Reject All
        btn_row2 = QHBoxLayout()
        btn_accept_all = QPushButton("Accept All")
        btn_reject_all = QPushButton("Reject All")
        btn_row2.addWidget(btn_accept_all)
        btn_row2.addWidget(btn_reject_all)
        left_layout.addLayout(btn_row2)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Stories")
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        left_layout.addWidget(self.tree)
        left_widget.setMinimumWidth(200)
        main_layout.addWidget(left_widget, 2)

        btn_expand.clicked.connect(self.expand_selected_item)
        btn_collapse.clicked.connect(self.collapse_selected_item)
        btn_accept_all.clicked.connect(self.accept_all_nodes_in_story)
        btn_reject_all.clicked.connect(self.reject_all_nodes_in_story)

    def update_status_bar(self):
        # Count all nodes and unapproved nodes across all stories
        total_nodes = 0
        unapproved_nodes = 0
        for story, nodes in self.state.items():
            if not isinstance(nodes, dict):
                continue
            for node, val in nodes.items():
                approved = val.get("approved") if isinstance(val, dict) else bool(val)
                total_nodes += 1
                if not approved:
                    unapproved_nodes += 1
        self.status_label_all.setText(f"All stories: {total_nodes} nodes, {unapproved_nodes} need approval")

        # Count for current story
        story = self.current_story
        story_total = 0
        story_unapproved = 0
        if story and story in self.state and isinstance(self.state[story], dict):
            for node, val in self.state[story].items():
                approved = val.get("approved") if isinstance(val, dict) else bool(val)
                story_total += 1
                if not approved:
                    story_unapproved += 1
        self.status_label_story.setText(f"  |  {story if story else ''}: {story_total} nodes, {story_unapproved} need approval")

        # Restore window geometry/state if available
        winstate = self.state.get("window", {})
        if winstate.get("maximized"):
            self.showMaximized()
    def accept_all_nodes_in_story(self):
        # Save expanded/collapsed state and selection
        expanded = set()
        selected = None
        def save_expanded(item, path):
            # Always use node names (Qt.UserRole) for path, not label text
            node_name = item.data(0, Qt.UserRole)
            new_path = path + [node_name] if node_name else path
            if item.isExpanded():
                expanded.add(tuple(new_path))
            for i in range(item.childCount()):
                save_expanded(item.child(i), new_path)
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            story_item = root.child(i)
            story_name = story_item.text(0)
            for j in range(story_item.childCount()):
                save_expanded(story_item.child(j), [story_name, story_item.child(j).data(0, Qt.UserRole)])
        current = self.tree.currentItem()
        if current:
            selected = []
            item2 = current
            while item2:
                selected.insert(0, item2.data(0, Qt.UserRole))
                item2 = item2.parent()

        item = self.tree.currentItem()
        if item is None:
            return
        # Find the top-level story item
        story_item = item
        while story_item.parent() is not None:
            story_item = story_item.parent()
        story = story_item.text(0)
        # Collect all node names under the selected item (including itself)
        node_names = []
        def collect_nodes(tree_item):
            # Only collect if not the top-level story item
            if tree_item != story_item:
                node_name = tree_item.data(0, Qt.UserRole)
                if node_name:
                    node_names.append(node_name)
            for i in range(tree_item.childCount()):
                collect_nodes(tree_item.child(i))
        collect_nodes(item)
        # If the selected item is a node, include it
        if item != story_item:
            node_name = item.data(0, Qt.UserRole)
            if node_name and node_name not in node_names:
                node_names.insert(0, node_name)
        # Update state for these nodes only
        for node_name in node_names:
            self.state.setdefault(story, {})[node_name] = True
        self.save_state()
        self.load_stories_with_restore(expanded, selected)

    def reject_all_nodes_in_story(self):
        # Save expanded/collapsed state and selection
        expanded = set()
        selected = None
        def save_expanded(item, path):
            if item.isExpanded():
                expanded.add(tuple(path))
            for i in range(item.childCount()):
                save_expanded(item.child(i), path + [item.child(i).data(0, Qt.UserRole)])
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            story_item = root.child(i)
            story_name = story_item.text(0)
            for j in range(story_item.childCount()):
                save_expanded(story_item.child(j), [story_name, story_item.child(j).data(0, Qt.UserRole)])
        current = self.tree.currentItem()
        if current:
            selected = []
            item2 = current
            while item2:
                selected.insert(0, item2.data(0, Qt.UserRole))
                item2 = item2.parent()

        item = self.tree.currentItem()
        if item is None:
            return
        # Find the top-level story item
        story_item = item
        while story_item.parent() is not None:
            story_item = story_item.parent()
        story = story_item.text(0)
        # Collect all node names under the selected item (including itself)
        node_names = []
        def collect_nodes(tree_item):
            # Only collect if not the top-level story item
            if tree_item != story_item:
                node_name = tree_item.data(0, Qt.UserRole)
                if node_name:
                    node_names.append(node_name)
            for i in range(tree_item.childCount()):
                collect_nodes(tree_item.child(i))
        collect_nodes(item)
        # If the selected item is a node, include it
        if item != story_item:
            node_name = item.data(0, Qt.UserRole)
            if node_name and node_name not in node_names:
                node_names.insert(0, node_name)
        # Update state for these nodes only
        for node_name in node_names:
            self.state.setdefault(story, {})[node_name] = False
        self.save_state()
        self.load_stories_with_restore(expanded, selected)
    def load_stories_with_restore(self, expanded, selected):
        # This is a copy of load_stories, but restores expanded/collapsed state and selection from arguments
        self.tree.clear()
        stories_dir = "stories"
        for story in os.listdir(stories_dir):
            story_path = os.path.join(stories_dir, story)
            if os.path.isdir(story_path):
                story_item = QTreeWidgetItem([story])
                story_item.setData(0, Qt.UserRole, None)
                story_json_path = os.path.join(story_path, "story.json")
                if not os.path.exists(story_json_path):
                    story_json_path = os.path.join(story_path, "..", "story.json")
                if os.path.exists(story_json_path):
                    with open(story_json_path, "r", encoding="utf-8") as f:
                        story_data = json.load(f)
                    nodes = story_data.get("nodes", {})
                    # Build parent map
                    parent_map = {k: set() for k in nodes}
                    for n, node in nodes.items():
                        for choice in node.get("choices", []):
                            next_node = choice.get("nextNode")
                            if next_node in parent_map:
                                parent_map[next_node].add(n)
                    # Add tree recursively
                    def add_node_recursive(node_name, parent_item, path=None, depth=0):
                        if path is None:
                            path = set()
                        if node_name in path or depth > 100:
                            return
                        path = set(path)
                        path.add(node_name)
                        node_state = self.state.get(story, {}).get(node_name, None)
                        node_hash = self._get_node_hash(story, node_name)
                        approved = False
                        if isinstance(node_state, dict):
                            # If hash doesn't match, auto-unapprove
                            if node_state.get("hash") != node_hash:
                                approved = False
                                # Update state to reflect unapproved
                                self.state.setdefault(story, {})[node_name] = {"approved": False, "hash": node_hash}
                            else:
                                approved = node_state.get("approved", False)
                        elif isinstance(node_state, bool):
                            # Legacy state: treat as approved/rejected, but update to new format
                            approved = node_state
                            self.state.setdefault(story, {})[node_name] = {"approved": approved, "hash": node_hash}
                        label = f"{node_name} {'✓' if approved else '✗'}"
                        node_item = QTreeWidgetItem([label])
                        node_item.setData(0, Qt.UserRole, node_name)
                        parent_item.addChild(node_item)
                        node = nodes.get(node_name)
                        if node and "choices" in node:
                            for choice in node["choices"]:
                                next_node = choice.get("nextNode")
                                if next_node:
                                    add_node_recursive(next_node, node_item, path, depth+1)
                    # Add all root nodes (nodes with no parents) except 'start'
                    roots = [n for n in nodes if not parent_map[n] and n != "start"]
                    if "start" in nodes:
                        add_node_recursive("start", story_item)
                    for orphan in roots:
                        add_node_recursive(orphan, story_item)
                self.tree.addTopLevelItem(story_item)
        # Restore expanded/collapsed state and selection
        def restore_expanded(item, path):
            # Always use node names (Qt.UserRole) for path, not label text
            node_name = item.data(0, Qt.UserRole)
            new_path = path + [node_name] if node_name else path
            if tuple(new_path) in expanded:
                item.setExpanded(True)
            for i in range(item.childCount()):
                restore_expanded(item.child(i), new_path)
        for i in range(self.tree.topLevelItemCount()):
            story_item = self.tree.topLevelItem(i)
            restore_expanded(story_item, [story_item.text(0)])
        # Restore selection
        if selected:
            def find_item(item, path, idx):
                if idx >= len(path):
                    return item
                for i in range(item.childCount()):
                    child = item.child(i)
                    if child.data(0, Qt.UserRole) == path[idx]:
                        return find_item(child, path, idx+1)
                return None
            for i in range(self.tree.topLevelItemCount()):
                story_item = self.tree.topLevelItem(i)
                if story_item.text(0) == selected[0]:
                    item = find_item(story_item, selected, 1)
                    if item:
                        self.tree.setCurrentItem(item)
                        break

    def _set_all_nodes_in_story(self, story, value):
        # Load story.json
        story_json_path = os.path.join("stories", story, "story.json")
        if not os.path.exists(story_json_path):
            story_json_path = os.path.join("stories", story, "..", "story.json")
        if not os.path.exists(story_json_path):
            return
        with open(story_json_path, "r", encoding="utf-8") as f:
            story_data = json.load(f)
        nodes = story_data.get("nodes", {})
        for node_name in nodes:
            self.state.setdefault(story, {})[node_name] = value
        self.save_state()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Stories")
        self.tree.itemClicked.connect(self.on_tree_item_clicked)

    def expand_selected_item(self):
        item = self.tree.currentItem()
        if item:
            self.expand_all_nodes(item)

    def collapse_selected_item(self):
        item = self.tree.currentItem()
        if item:
            self.collapse_all_nodes(item)
    def on_tree_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if item is None:
            return
        # Only show menu for top-level (story) items
        if item.parent() is not None:
            return
        menu = QMenu(self.tree)
        expand_action = menu.addAction("Expand All Nodes")
        collapse_action = menu.addAction("Collapse All Nodes")
        action = menu.exec_(self.tree.viewport().mapToGlobal(pos))
        if action == expand_action:
            self.expand_all_nodes(item)
        elif action == collapse_action:
            self.collapse_all_nodes(item)

    def expand_all_nodes(self, item):
        item.setExpanded(True)
        for i in range(item.childCount()):
            self.expand_all_nodes(item.child(i))

    def collapse_all_nodes(self, item):
        item.setExpanded(False)
        for i in range(item.childCount()):
            self.collapse_all_nodes(item.child(i))
    def __init__(self):
        super().__init__()
        from PySide6.QtWidgets import QLabel
        self.status_bar = self.statusBar()
        self.status_label_all = QLabel()
        self.status_label_story = QLabel()
        self.status_bar.addWidget(self.status_label_all)
        self.status_bar.addWidget(self.status_label_story)
        self.state = self.load_state()
        self.current_story = None
        self.current_node = None
        self.text_size = 12
        # Layouts
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Left: Tree with control buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Top row: Refresh and Publish
        btn_top_row = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Stories")
        self.publish_btn = QPushButton("Publish Story")
        btn_top_row.addWidget(self.refresh_btn)
        btn_top_row.addWidget(self.publish_btn)
        left_layout.addLayout(btn_top_row)

        # Middle row: Accept/Reject All
        btn_row2 = QHBoxLayout()
        btn_accept_all = QPushButton("Accept All")
        btn_reject_all = QPushButton("Reject All")
        btn_row2.addWidget(btn_accept_all)
        btn_row2.addWidget(btn_reject_all)
        left_layout.addLayout(btn_row2)

        # Bottom row: Expand/Collapse
        btn_row = QHBoxLayout()
        btn_expand = QPushButton("Expand All")
        btn_collapse = QPushButton("Collapse All")
        btn_row.addWidget(btn_expand)
        btn_row.addWidget(btn_collapse)
        left_layout.addLayout(btn_row)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Stories")
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        left_layout.addWidget(self.tree)
        left_widget.setMinimumWidth(200)
        main_layout.addWidget(left_widget, 2)

        btn_expand.clicked.connect(self.expand_selected_item)
        btn_collapse.clicked.connect(self.collapse_selected_item)
        btn_accept_all.clicked.connect(self.accept_all_nodes_in_story)
        btn_reject_all.clicked.connect(self.reject_all_nodes_in_story)

    # (Removed duplicate left panel and tree creation)

        # Right: Single bottom pane (no rendered_view)
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        self.filename_label = QLabel("")
        bottom_layout.addWidget(self.filename_label)
        self.text_edit = QTextEdit()
        font = QFont()
        font.setPointSize(self.text_size)
        self.text_edit.setFont(font)
        bottom_layout.addWidget(self.text_edit)

        # Choice buttons row (initially empty, will be filled by render_node_with_choices)
        self._choice_btn_row = QWidget()
        self._choice_btn_layout = QHBoxLayout(self._choice_btn_row)
        self._choice_btn_layout.setContentsMargins(0, 8, 0, 0)
        self._choice_btn_layout.setSpacing(8)
        bottom_layout.addWidget(self._choice_btn_row)

        btn_layout = QHBoxLayout()
        self.accept_btn = QPushButton("Accept and stay")  # Underline C for Ctrl+Return
        self.reject_btn = QPushButton("Reject and stay")  # Underline J for Ctrl+Backspace
        self.save_btn = QPushButton("Sa&ve")      # Underline V for Ctrl+S
        btn_layout.addWidget(self.accept_btn)
        btn_layout.addWidget(self.reject_btn)
        btn_layout.addWidget(self.save_btn)
        bottom_layout.addLayout(btn_layout)
        main_layout.addWidget(bottom_widget, 5)

    # (Removed: buttons from main_layout, now in left_layout)

        # Connect buttons
        self.accept_btn.clicked.connect(self.accept_node)
        self.reject_btn.clicked.connect(self.reject_node)
        self.save_btn.clicked.connect(self.save_node)
        self.publish_btn.clicked.connect(self.publish_story)
        self.refresh_btn.clicked.connect(self.load_stories)
        self.text_edit.textChanged.connect(self.update_rendered_view)

        # Menu for text size and refresh (after widgets are created)
        menubar = self.menuBar()
        view_menu = menubar.addMenu("View")
        increase_font_action = QAction("Increase Text Size", self)
        decrease_font_action = QAction("Decrease Text Size", self)
        refresh_stories_action = QAction("Refresh Stories", self)
        view_menu.addAction(increase_font_action)
        view_menu.addAction(decrease_font_action)
        view_menu.addSeparator()
        view_menu.addAction(refresh_stories_action)
        increase_font_action.setShortcut("Ctrl++")
        decrease_font_action.setShortcut("Ctrl+-")
        increase_font_action.triggered.connect(self.increase_text_size)
        decrease_font_action.triggered.connect(self.decrease_text_size)
        refresh_stories_action.triggered.connect(self.load_stories)

        # Keyboard shortcuts for buttons (after buttons are created)
        self.accept_btn.setShortcut("Ctrl+Return")
        self.reject_btn.setShortcut("Ctrl+Backspace")
        self.save_btn.setShortcut("Ctrl+S")

        # Load stories and populate tree
        self.load_stories()
    def increase_text_size(self):
        self.text_size = min(self.text_size + 2, 48)
        self.update_fonts()

    def decrease_text_size(self):
        self.text_size = max(self.text_size - 2, 8)
        self.update_fonts()

    def update_fonts(self):
        font = QFont()
        font.setPointSize(self.text_size)
        self.text_edit.setFont(font)
        self.rendered_view.setFont(font)

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_state(self):
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def load_stories(self):
        # Save expanded/collapsed state and selection
        expanded = set()
        selected = None
        def save_expanded(item, path):
            if item.isExpanded():
                expanded.add(tuple(path))
            for i in range(item.childCount()):
                save_expanded(item.child(i), path + [item.child(i).data(0, Qt.UserRole)])
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            story_item = root.child(i)
            story_name = story_item.text(0)
            for j in range(story_item.childCount()):
                save_expanded(story_item.child(j), [story_name, story_item.child(j).data(0, Qt.UserRole)])
        current = self.tree.currentItem()
        if current:
            selected = []
            item = current
            while item:
                selected.insert(0, item.data(0, Qt.UserRole))
                item = item.parent()
        self.tree.clear()
        stories_dir = "stories"
        for story in os.listdir(stories_dir):
            story_path = os.path.join(stories_dir, story)
            if os.path.isdir(story_path):
                story_item = QTreeWidgetItem([story])
                story_item.setData(0, Qt.UserRole, None)
                story_json_path = os.path.join(story_path, "story.json")
                if not os.path.exists(story_json_path):
                    story_json_path = os.path.join(story_path, "..", "story.json")
                if os.path.exists(story_json_path):
                    with open(story_json_path, "r", encoding="utf-8") as f:
                        story_data = json.load(f)
                    nodes = story_data.get("nodes", {})
                    # Build parent map
                    parent_map = {k: set() for k in nodes}
                    for n, node in nodes.items():
                        for choice in node.get("choices", []):
                            next_node = choice.get("nextNode")
                            if next_node in parent_map:
                                parent_map[next_node].add(n)
                    # Add tree recursively
                    def add_node_recursive(node_name, parent_item, path=None, depth=0):
                        if path is None:
                            path = set()
                        if node_name in path or depth > 100:
                            return
                        path = set(path)
                        path.add(node_name)
                        proofed = self.state.get(story, {}).get(node_name, False)
                        label = f"{node_name} {'✓' if proofed else '✗'}"
                        node_item = QTreeWidgetItem([label])
                        node_item.setData(0, Qt.UserRole, node_name)
                        parent_item.addChild(node_item)
                        node = nodes.get(node_name)
                        if node and "choices" in node:
                            for choice in node["choices"]:
                                next_node = choice.get("nextNode")
                                if next_node:
                                    add_node_recursive(next_node, node_item, path, depth+1)
                    # Add all root nodes (nodes with no parents) except 'start'
                    roots = [n for n in nodes if not parent_map[n] and n != "start"]
                    if "start" in nodes:
                        add_node_recursive("start", story_item)
                    for orphan in roots:
                        add_node_recursive(orphan, story_item)
                self.tree.addTopLevelItem(story_item)
        # Restore expanded/collapsed state and selection
        def restore_expanded(item, path):
            if tuple(path) in expanded:
                item.setExpanded(True)
            for i in range(item.childCount()):
                restore_expanded(item.child(i), path + [item.child(i).data(0, Qt.UserRole)])
        for i in range(self.tree.topLevelItemCount()):
            story_item = self.tree.topLevelItem(i)
            restore_expanded(story_item, [story_item.text(0)])
        # Restore selection
        if selected:
            def find_item(item, path, idx):
                if idx >= len(path):
                    return item
                for i in range(item.childCount()):
                    child = item.child(i)
                    if child.data(0, Qt.UserRole) == path[idx]:
                        return find_item(child, path, idx+1)
                return None
            for i in range(self.tree.topLevelItemCount()):
                story_item = self.tree.topLevelItem(i)
                if story_item.text(0) == selected[0]:
                    item = find_item(story_item, selected, 1)
                    if item:
                        self.tree.setCurrentItem(item)
                        break
        self.update_status_bar()

    def accept_node(self):
        if self.current_story and self.current_node:
            node_hash = self._get_node_hash(self.current_story, self.current_node)
            self.state.setdefault(self.current_story, {})[self.current_node] = {
                "approved": True,
                "hash": node_hash
            }
            self.save_state()
            # Update label for current node in tree
            item = self.tree.currentItem()
            if item:
                label = item.text(0)
                if label.endswith('✗'):
                    item.setText(0, label[:-1] + '✓')
                elif label.endswith('✓'):
                    pass  # already accepted
                else:
                    item.setText(0, label + ' ✓')
            self.update_status_bar()

    def reject_node(self):
        if self.current_story and self.current_node:
            node_hash = self._get_node_hash(self.current_story, self.current_node)
            self.state.setdefault(self.current_story, {})[self.current_node] = {
                "approved": False,
                "hash": node_hash
            }
            self.save_state()
            # Update label for current node in tree
            item = self.tree.currentItem()
            if item:
                label = item.text(0)
                if label.endswith('✓'):
                    item.setText(0, label[:-1] + '✗')
                elif label.endswith('✗'):
                    pass  # already rejected
                else:
                    item.setText(0, label + ' ✗')
            self.update_status_bar()

    def on_tree_item_clicked(self, item, column):
        node = item.data(0, Qt.UserRole)
        if node is None:
            # This is a story root (no node name)
            self.filename_label.setText("")
            self.current_story = item.text(0)
            self.current_node = None
            self.update_status_bar()
            return
        # Traverse up to the story root
        story_item = item
        while story_item.parent() is not None:
            story_item = story_item.parent()
        story = story_item.text(0)
        self.current_story = story
        self.current_node = node
        node_path = os.path.join("stories", story, "nodes", f"{node}.txt")
        self.filename_label.setText(node_path)
        if os.path.exists(node_path):
            with open(node_path, "r", encoding="utf-8") as f:
                text = f.read()
            self.text_edit.setPlainText(text)
            self.render_node_with_choices(text)
        else:
            self.text_edit.setPlainText("")
            self.rendered_view.setText("")
        self.update_status_bar()

    def save_node(self):
        if self.current_story and self.current_node:
            node_path = os.path.join("stories", self.current_story, "nodes", f"{self.current_node}.txt")
            with open(node_path, "w", encoding="utf-8") as f:
                f.write(self.text_edit.toPlainText())
            # Ensure rendered view uses correct font size and choices rendering
            self.render_node_with_choices(self.text_edit.toPlainText())

    def accept_node(self):
        if self.current_story and self.current_node:
            node_hash = self._get_node_hash(self.current_story, self.current_node)
            self.state.setdefault(self.current_story, {})[self.current_node] = {
                "approved": True,
                "hash": node_hash
            }
            self.save_state()
            # Update label for current node in tree
            item = self.tree.currentItem()
            if item:
                label = item.text(0)
                if label.endswith('✗'):
                    item.setText(0, label[:-1] + '✓')
                elif label.endswith('✓'):
                    pass  # already accepted
                else:
                    item.setText(0, label + ' ✓')
            self.update_status_bar()

    def reject_node(self):
        if self.current_story and self.current_node:
            node_hash = self._get_node_hash(self.current_story, self.current_node)
            self.state.setdefault(self.current_story, {})[self.current_node] = {
                "approved": False,
                "hash": node_hash
            }
            self.save_state()
            # Update label for current node in tree
            item = self.tree.currentItem()
            if item:
                label = item.text(0)
                if label.endswith('✓'):
                    item.setText(0, label[:-1] + '✗')
                elif label.endswith('✗'):
                    pass  # already rejected
                else:
                    item.setText(0, label + ' ✗')
            self.update_status_bar()

    def update_rendered_view(self):
        self.render_node_with_choices(self.text_edit.toPlainText())

    def render_node_with_choices(self, text):
        # Remove any previous choice buttons from the row
        if hasattr(self, '_choice_btns') and self._choice_btns:
            for btn in self._choice_btns:
                self._choice_btn_layout.removeWidget(btn)
                btn.setParent(None)
        self._choice_btns = []

        # Add choices as real QPushButton widgets below the text editor
        if self.current_story and self.current_node:
            story_json_path = os.path.join("stories", self.current_story, "story.json")
            if not os.path.exists(story_json_path):
                story_json_path = os.path.join("stories", self.current_story, "..", "story.json")
            if os.path.exists(story_json_path):
                with open(story_json_path, "r", encoding="utf-8") as f:
                    story_data = json.load(f)
                node_data = story_data.get("nodes", {}).get(self.current_node, {})
                choices = node_data.get("choices", [])
                for idx, choice in enumerate(choices):
                    btn = QPushButton(f"Accept and: {choice['text']}")
                    btn.setStyleSheet("")  # Use default QPushButton style
                    shortcut = str(idx+1) if idx < 9 else None
                    if shortcut:
                        btn.setShortcut(shortcut)
                    btn.clicked.connect(lambda checked, i=idx: self.handle_choice_button(i))
                    self._choice_btn_layout.addWidget(btn)
                    self._choice_btns.append(btn)

    def handle_choice_button(self, idx):
        # Accept and advance to the next node
        story_json_path = os.path.join("stories", self.current_story, "story.json")
        if not os.path.exists(story_json_path):
            story_json_path = os.path.join("stories", self.current_story, "..", "story.json")
        if os.path.exists(story_json_path):
            with open(story_json_path, "r", encoding="utf-8") as f:
                story_data = json.load(f)
            node_data = story_data.get("nodes", {}).get(self.current_node, {})
            choices = node_data.get("choices", [])
            if 0 <= idx < len(choices):
                next_node = choices[idx].get("nextNode")
                if next_node:
                    self.accept_node()
                    # Find and select the next node in the tree
                    self.select_node_in_tree(self.current_story, next_node)

    def handle_choice_link(self, link):
        # Accept and advance to the next node
        if link.startswith("choice_"):
            idx = int(link.split("_")[1])
            story_json_path = os.path.join("stories", self.current_story, "story.json")
            if not os.path.exists(story_json_path):
                story_json_path = os.path.join("stories", self.current_story, "..", "story.json")
            if os.path.exists(story_json_path):
                with open(story_json_path, "r", encoding="utf-8") as f:
                    story_data = json.load(f)
                node_data = story_data.get("nodes", {}).get(self.current_node, {})
                choices = node_data.get("choices", [])
                if 0 <= idx < len(choices):
                    next_node = choices[idx].get("nextNode")
                    if next_node:
                        self.accept_node()
                        # Find and select the next node in the tree
                        self.select_node_in_tree(self.current_story, next_node)

    def select_node_in_tree(self, story, node):
        # Traverse the tree to find and select the node
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            story_item = root.child(i)
            if story_item.text(0) == story:
                self._select_node_recursive(story_item, node)

    def _select_node_recursive(self, item, node):
        for i in range(item.childCount()):
            child = item.child(i)
            if child.text(0).startswith(node + " ") or child.text(0) == node:
                self.tree.setCurrentItem(child)
                self.on_tree_item_clicked(child, 0)
                return True
            if self._select_node_recursive(child, node):
                return True
        return False

    def publish_story(self):
        if not self.current_story:
            QMessageBox.warning(self, "No Story Selected", "Please select a story to publish.")
            return
        story_dir = os.path.join("stories", self.current_story)
        story_json_path = os.path.join(story_dir, "story.json")
        # Try to find the main story.json (in root or in story dir)
        if not os.path.exists(story_json_path):
            # fallback to root
            story_json_path = os.path.join(story_dir, "..", "story.json")
        if not os.path.exists(story_json_path):
            QMessageBox.warning(self, "No story.json", f"No story.json found for {self.current_story}.")
            return
        with open(story_json_path, "r", encoding="utf-8") as f:
            story_data = json.load(f)
        # Update node texts
        nodes_dir = os.path.join(story_dir, "nodes")
        for node_name in story_data.get("nodes", {}):
            node_file = os.path.join(nodes_dir, f"{node_name}.txt")
            if os.path.exists(node_file):
                with open(node_file, "r", encoding="utf-8") as nf:
                    story_data["nodes"][node_name]["text"] = nf.read()
        # Save updated story.json
        with open(story_json_path, "w", encoding="utf-8") as f:
            json.dump(story_data, f, indent=2, ensure_ascii=False)
        QMessageBox.information(self, "Published", f"Story '{self.current_story}' published to story.json.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProofReaderApp()
    window.show()
    sys.exit(app.exec())
