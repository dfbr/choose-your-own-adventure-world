import sys
import os
import json
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget,
    QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QSplitter, QFileDialog, QMessageBox, QMenu
)
from PySide6.QtCore import Qt


STATE_FILE = "state.json"

class ProofReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = self.load_state()
        self.current_story = None
        self.current_node = None
        self.text_size = 12
        # Layouts
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Left: Tree with expand/collapse buttons

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        btn_row = QHBoxLayout()
        btn_expand = QPushButton("Expand All")
        btn_collapse = QPushButton("Collapse All")
        btn_accept_all = QPushButton("Accept All")
        btn_reject_all = QPushButton("Reject All")
        btn_row.addWidget(btn_expand)
        btn_row.addWidget(btn_collapse)
        left_layout.addLayout(btn_row)
        btn_row2 = QHBoxLayout()
        btn_row2.addWidget(btn_accept_all)
        btn_row2.addWidget(btn_reject_all)
        left_layout.addLayout(btn_row2)
        btn_accept_all.clicked.connect(self.accept_all_nodes_in_story)
        btn_reject_all.clicked.connect(self.reject_all_nodes_in_story)

    def accept_all_nodes_in_story(self):
        item = self.tree.currentItem()
        if item is None:
            return
        # Find the top-level story item
        while item.parent() is not None:
            item = item.parent()
        story = item.text(0)
        # Accept all nodes in this story
        self._set_all_nodes_in_story(story, True)
        self.load_stories()

    def reject_all_nodes_in_story(self):
        item = self.tree.currentItem()
        if item is None:
            return
        # Find the top-level story item
        while item.parent() is not None:
            item = item.parent()
        story = item.text(0)
        # Reject all nodes in this story
        self._set_all_nodes_in_story(story, False)
        self.load_stories()

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
        left_layout.addWidget(self.tree)
        left_widget.setMinimumWidth(200)
        main_layout.addWidget(left_widget, 2)

        btn_expand.clicked.connect(self.expand_selected_item)
        btn_collapse.clicked.connect(self.collapse_selected_item)

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
        self.state = self.load_state()
        self.current_story = None
        self.current_node = None
        self.text_size = 12
        # Layouts
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Left: Tree with expand/collapse buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
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

        # Right: Splitter for top/bottom panes
        right_splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(right_splitter, 5)

        # Top: Rendered view
        self.rendered_view = QLabel("Rendered node will appear here")
        self.rendered_view.setWordWrap(True)
        self.rendered_view.setAlignment(Qt.AlignTop)
        self.rendered_view.setTextFormat(Qt.RichText)
        right_splitter.addWidget(self.rendered_view)

        # Bottom: Editable text with filename label
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        self.filename_label = QLabel("")
        bottom_layout.addWidget(self.filename_label)
        self.text_edit = QTextEdit()
        font = QFont()
        font.setPointSize(self.text_size)
        self.text_edit.setFont(font)
        bottom_layout.addWidget(self.text_edit)
        btn_layout = QHBoxLayout()
        self.accept_btn = QPushButton("A&ccept")  # Underline C for Ctrl+Return
        self.reject_btn = QPushButton("Re&ject")  # Underline J for Ctrl+Backspace
        self.save_btn = QPushButton("Sa&ve")      # Underline V for Ctrl+S
        btn_layout.addWidget(self.accept_btn)
        btn_layout.addWidget(self.reject_btn)
        btn_layout.addWidget(self.save_btn)
        bottom_layout.addLayout(btn_layout)
        right_splitter.addWidget(bottom_widget)


    # Refresh Stories button
    self.refresh_btn = QPushButton("Refresh Stories")
    main_layout.addWidget(self.refresh_btn, 0, Qt.AlignBottom)

    # Publish button
    self.publish_btn = QPushButton("Publish Story")
    main_layout.addWidget(self.publish_btn, 0, Qt.AlignBottom)


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

    def on_tree_item_clicked(self, item, column):
        node = item.data(0, Qt.UserRole)
        if node is None:
            # This is a story root (no node name)
            self.filename_label.setText("")
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

    def save_node(self):
        if self.current_story and self.current_node:
            node_path = os.path.join("stories", self.current_story, "nodes", f"{self.current_node}.txt")
            with open(node_path, "w", encoding="utf-8") as f:
                f.write(self.text_edit.toPlainText())
            # Ensure rendered view uses correct font size and choices rendering
            self.render_node_with_choices(self.text_edit.toPlainText())

    def accept_node(self):
        if self.current_story and self.current_node:
            self.state.setdefault(self.current_story, {})[self.current_node] = True
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

    def reject_node(self):
        if self.current_story and self.current_node:
            self.state.setdefault(self.current_story, {})[self.current_node] = False
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

    def update_rendered_view(self):
        self.render_node_with_choices(self.text_edit.toPlainText())

    def render_node_with_choices(self, text):
        # Render node text and choices as buttons
        html = f'<div style="font-size:{self.text_size}pt;">{text.replace("\n", "<br>")}</div>'
        # Add choices as buttons if possible
        if self.current_story and self.current_node:
            # Find choices for this node
            story_json_path = os.path.join("stories", self.current_story, "story.json")
            if not os.path.exists(story_json_path):
                story_json_path = os.path.join("stories", self.current_story, "..", "story.json")
            if os.path.exists(story_json_path):
                with open(story_json_path, "r", encoding="utf-8") as f:
                    story_data = json.load(f)
                node_data = story_data.get("nodes", {}).get(self.current_node, {})
                choices = node_data.get("choices", [])
                if choices:
                    html += "<hr>"
                    for idx, choice in enumerate(choices):
                        btn_html = f'<button onclick="py:choice_{idx}()">{choice["text"]}</button>'
                        html += btn_html + " "
        self.rendered_view.setText(html)
        # Dynamically connect buttons (simulate with QLabel linkActivated)
        if self.current_story and self.current_node:
            story_json_path = os.path.join("stories", self.current_story, "story.json")
            if not os.path.exists(story_json_path):
                story_json_path = os.path.join("stories", self.current_story, "..", "story.json")
            if os.path.exists(story_json_path):
                with open(story_json_path, "r", encoding="utf-8") as f:
                    story_data = json.load(f)
                node_data = story_data.get("nodes", {}).get(self.current_node, {})
                choices = node_data.get("choices", [])
                # QLabel doesn't support real buttons, so use links
                if choices:
                    html = f'<div style="font-size:{self.text_size}pt;">{text.replace("\n", "<br>")}</div><hr>'
                    for idx, choice in enumerate(choices):
                        html += f'<a href="choice_{idx}"><button>{choice["text"]}</button></a> '
                    self.rendered_view.setTextFormat(Qt.RichText)
                    self.rendered_view.setText(html)
                    self.rendered_view.setOpenExternalLinks(False)
                    self.rendered_view.linkActivated.connect(self.handle_choice_link)

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
