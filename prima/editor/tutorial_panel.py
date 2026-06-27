from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QTextBrowser, QSplitter, QLabel, QPushButton
)
from PyQt5.QtCore import Qt
from prima.tutorials.themes import THEME_TUTORIALS
from prima.tutorials.lessons import ENGINE_LESSONS

INTERACTIVE_TOUR_KEYS = {
    "Getting Started with Prima": "getting_started",
}


class TutorialPanel(QWidget):
    def __init__(self, engine=None, parent=None, start_tour_callback=None):
        super().__init__(parent)
        self.engine = engine
        self._start_tour_callback = start_tour_callback
        self._current_lesson = None
        self._current_theme_step = None
        self._current_theme_index = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Vertical)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Prima Tutorials & Lessons")
        self.tree.itemClicked.connect(self._on_item_clicked)
        splitter.addWidget(self.tree)

        self.content = QTextBrowser()
        self.content.setOpenExternalLinks(True)
        self.content.setStyleSheet("""
            QTextBrowser {
                background: #1e1e1e; color: #d4d4d4;
                font-family: 'Segoe UI', sans-serif; font-size: 13px;
                padding: 16px;
            }
            QTextBrowser h1 { color: #569cd6; font-size: 20px; }
            QTextBrowser h2 { color: #4ec9b0; font-size: 16px; }
            QTextBrowser h3 { color: #c586c0; font-size: 14px; }
            QTextBrowser code {
                background: #2d2d2d; color: #ce9178;
                padding: 2px 6px; border-radius: 3px;
                font-family: 'Consolas', monospace; font-size: 12px;
            }
            QTextBrowser pre {
                background: #252526; color: #d4d4d4;
                padding: 12px; border-left: 3px solid #569cd6;
                font-family: 'Consolas', monospace; font-size: 12px;
            }
        """)
        splitter.addWidget(self.content)

        btn_bar = QHBoxLayout()
        self._tour_btn = QPushButton("Start Interactive Tour")
        self._tour_btn.setStyleSheet("""
            QPushButton { background: #2d7d2d; color: white; border: none; padding: 4px 12px; border-radius: 3px; font-weight: bold; }
            QPushButton:hover { background: #3a9a3a; }
        """)
        self._tour_btn.clicked.connect(self._start_tour)
        self._tour_btn.setVisible(False)
        self._run_btn = QPushButton("Run Example")
        self._run_btn.clicked.connect(self._run_example)
        self._run_btn.setEnabled(False)
        self._apply_btn = QPushButton("Apply to Scene")
        self._apply_btn.clicked.connect(self._apply_lesson)
        self._apply_btn.setEnabled(False)
        btn_bar.addWidget(self._tour_btn)
        btn_bar.addWidget(self._run_btn)
        btn_bar.addWidget(self._apply_btn)
        btn_bar.addStretch()

        btn_widget = QWidget()
        btn_widget.setLayout(btn_bar)
        splitter.addWidget(btn_widget)

        layout.addWidget(splitter)

        self._populate()

    def _populate(self):
        tut_root = QTreeWidgetItem(self.tree, ["Tutorials by Theme"])
        tut_root.setExpanded(True)

        for theme in THEME_TUTORIALS:
            theme_item = QTreeWidgetItem(tut_root, [theme["title"]])
            theme_item.setData(0, Qt.UserRole, ("theme_index", THEME_TUTORIALS.index(theme)))
            for step in theme.get("steps", []):
                step_item = QTreeWidgetItem(theme_item, [step["title"]])
                step_item.setData(0, Qt.UserRole, ("theme_step", THEME_TUTORIALS.index(theme), theme["steps"].index(step)))

        les_root = QTreeWidgetItem(self.tree, ["Engine Lessons"])
        les_root.setExpanded(True)

        cats = {}
        for lesson in ENGINE_LESSONS:
            cat = lesson.get("category", "General")
            if cat not in cats:
                cat_item = QTreeWidgetItem(les_root, [cat])
                cats[cat] = cat_item
            les_item = QTreeWidgetItem(cats[cat], [lesson["title"]])
            les_item.setData(0, Qt.UserRole, ("lesson", ENGINE_LESSONS.index(lesson)))

    def _on_item_clicked(self, item, col):
        data = item.data(0, Qt.UserRole)
        if data is None:
            return

        self._current_lesson = None
        self._current_theme_step = None

        kind = data[0]
        html = ""

        if kind == "theme_index":
            theme = THEME_TUTORIALS[data[1]]
            html = f"""<h1>Theme: {theme['title']}</h1>
<p>{theme.get('description', '')}</p>
<h3>Overview</h3>
<p>{theme.get('overview', '')}</p>
<h3>Steps ({len(theme.get('steps', []))})</h3>
<ul>
"""
            for i, s in enumerate(theme.get("steps", [])):
                html += f"<li><b>{i+1}. {s['title']}</b></li>"
            html += "</ul>"

        elif kind == "theme_step":
            theme = THEME_TUTORIALS[data[1]]
            step = theme["steps"][data[2]]
            self._current_theme_step = step
            html = f"""<h1>{step['title']}</h1>
<hr>
{step.get('content', '<p>Content coming soon.</p>')}
"""
            if "code" in step:
                html += f"<h3>Example Code</h3><pre>{step['code']}</pre>"
            if "tip" in step:
                html += f"<p><b>Tip:</b> {step['tip']}</p>"

        elif kind == "lesson":
            lesson = ENGINE_LESSONS[data[1]]
            self._current_lesson = lesson
            html = f"""<h1>{lesson['title']}</h1>
<h3>Category: {lesson.get('category', 'General')}</h3>
<hr>
{lesson.get('content', '<p>Content coming soon.</p>')}
"""
            if "example" in lesson:
                html += f"<h3>Example</h3><pre>{lesson['example']}</pre>"
            if "notes" in lesson:
                html += f"<p><b>Notes:</b> {lesson['notes']}</p>"

        self.content.setHtml(html)

        self._tour_btn.setVisible(False)
        self._run_btn.setVisible(False)
        self._apply_btn.setVisible(False)

        if kind == "theme_index":
            theme = THEME_TUTORIALS[data[1]]
            tour_key = INTERACTIVE_TOUR_KEYS.get(theme["title"])
            self._current_theme_index = data[1]
            if tour_key:
                self._tour_btn.setVisible(True)
            show_lesson_btns = bool(tour_key)
            self._run_btn.setVisible(show_lesson_btns)
            self._apply_btn.setVisible(show_lesson_btns)
        elif kind == "theme_step":
            theme = THEME_TUTORIALS[data[1]]
            tour_key = INTERACTIVE_TOUR_KEYS.get(theme["title"])
            if tour_key:
                self._tour_btn.setVisible(True)
            self._run_btn.setVisible(True)
            self._run_btn.setEnabled(bool(self._current_theme_step.get("code")))
            self._apply_btn.setVisible(False)
        elif kind == "lesson":
            self._run_btn.setVisible(True)
            self._run_btn.setEnabled(bool(self._current_lesson.get("example")))
            self._apply_btn.setVisible(True)
            self._apply_btn.setEnabled(self._current_lesson is not None)

    def set_tour_callback(self, callback):
        self._start_tour_callback = callback

    def _start_tour(self):
        if not self._start_tour_callback or self._current_theme_index is None:
            return
        theme = THEME_TUTORIALS[self._current_theme_index]
        tour_key = INTERACTIVE_TOUR_KEYS.get(theme["title"])
        if tour_key:
            self._start_tour_callback(tour_key)

    def _run_example(self):
        if not self.engine:
            return
        code = ""
        if self._current_lesson:
            code = self._current_lesson.get("example", "")
        elif self._current_theme_step:
            code = self._current_theme_step.get("code", "")
        if not code:
            return

        locals_dict = {
            "engine": self.engine,
            "scene": self.engine.scene,
        }
        try:
            exec(code, globals(), locals_dict)
        except Exception as e:
            print(f"Example error: {e}")

    def _apply_lesson(self):
        if not self.engine or not self._current_lesson:
            return
        title = self._current_lesson.get("title", "")
        example = self._current_lesson.get("example", "")

        if title == "scene.gravity" and "scene.gravity = " in example:
            for line in example.split("\n"):
                line = line.split("#")[0].strip()
                if line.startswith("scene.gravity"):
                    exec(line, {"scene": self.engine.scene, "Vector3": __import__("prima.engine.math_utils", fromlist=["Vector3"]).Vector3})
                    break
        elif title == "scene.physics_enabled" and "scene.physics_enabled = " in example:
            for line in example.split("\n"):
                line = line.split("#")[0].strip()
                if line.startswith("scene.physics_enabled"):
                    exec(line, {"scene": self.engine.scene})
                    break
        elif title == "scene.solver_iterations" and "scene.solver_iterations = " in example:
            for line in example.split("\n"):
                line = line.split("#")[0].strip()
                if line.startswith("scene.solver_iterations"):
                    exec(line, {"scene": self.engine.scene})
                    break
        elif title == "scene.linear_damping" and "scene.linear_damping = " in example:
            for line in example.split("\n"):
                line = line.split("#")[0].strip()
                if line.startswith("scene.linear_damping"):
                    exec(line, {"scene": self.engine.scene})
                    break
        elif title == "scene.angular_damping" and "scene.angular_damping = " in example:
            for line in example.split("\n"):
                line = line.split("#")[0].strip()
                if line.startswith("scene.angular_damping"):
                    exec(line, {"scene": self.engine.scene})
                    break
        elif title.startswith("obj."):
            obj = self.engine.scene.find_by_name("Ground")
            if obj:
                for line in example.split("\n"):
                    line = line.split("#")[0].strip()
                    if line.startswith("obj."):
                        exec(line, {"obj": obj, "Vector3": __import__("prima.engine.math_utils", fromlist=["Vector3"]).Vector3})
                        break
        elif title.startswith("engine."):
            for line in example.split("\n"):
                line = line.split("#")[0].strip()
                if line.startswith("engine."):
                    exec(line, {"engine": self.engine})
                    break
        elif title.startswith("camera."):
            root = self.engine.scene.root
            for child in root.children:
                if child.object_type == "Camera":
                    for line in example.split("\n"):
                        line = line.split("#")[0].strip()
                        if line.startswith("cam."):
                            exec(line.replace("cam.", "camera."), {"camera": child})
                            break
                    break
        elif title.startswith("light."):
            root = self.engine.scene.root
            for child in root.children:
                if child.object_type == "Light":
                    for line in example.split("\n"):
                        line = line.split("#")[0].strip()
                        if line.startswith("light."):
                            exec(line.replace("light.", "light_obj."), {"light_obj": child})
                            break
                    break
        elif title.startswith("part."):
            root = self.engine.scene.root
            for child in root.children:
                if child.object_type in ("Part", "Sphere"):
                    for line in example.split("\n"):
                        line = line.split("#")[0].strip()
                        if line.startswith("part."):
                            exec(line.replace("part.", "part_obj."), {"part_obj": child, "Vector3": __import__("prima.engine.math_utils", fromlist=["Vector3"]).Vector3})
                            break
                    break

        self.engine.scene.root._mark_dirty()
