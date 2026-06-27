from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QApplication,
)
from PyQt5.QtCore import Qt, QTimer, QRect, QObject
from PyQt5.QtGui import QFont, QColor, QPalette


TOURS = {
    "getting_started": {
        "title": "Getting Started with Prima",
        "steps": [
            {
                "title": "Welcome",
                "text": "<h2>Welcome to Prima!</h2><p>This interactive tour will show you around the Prima editor. You'll learn the key panels and how to use them.</p><p>Click <b>Next</b> to begin.</p>",
                "highlight": None,
                "wait": "next",
            },
            {
                "title": "3D Viewport",
                "text": "<p>This is the <b>3D Viewport</b> — the main area where you build and view your 3D scene.</p><p><b>Try it now:</b> Hold the <b>Right Mouse Button</b> and drag to orbit around the scene.</p>",
                "highlight": "viewport",
                "wait": "orbit",
            },
            {
                "title": "Scene Hierarchy",
                "text": "<p>The <b>Hierarchy Panel</b> on the left shows all objects in your scene.</p><p><b>Click</b> on <b>'Ground'</b> in the hierarchy to select it.</p>",
                "highlight": "hierarchy",
                "wait": "select:Ground",
            },
            {
                "title": "Properties Panel",
                "text": "<p>Great! The <b>Properties Panel</b> on the right now shows the selected object's settings.</p><p>You can change Position, Rotation, Size, Material, and Physics properties here.</p>",
                "highlight": "properties",
                "wait": "next",
            },
            {
                "title": "Transform Properties",
                "text": "<p>Try modifying the Ground's position: click the <b>Y spinbox</b> under Position and change the value.</p><p>Watch the viewport update as you edit.</p>",
                "highlight": "properties",
                "wait": "property_change",
            },
            {
                "title": "Playing the Scene",
                "text": "<p>Now let's see the physics in action! Click the <b>Play</b> button in the toolbar (or press <b>F5</b>).</p><p>This opens a separate runtime window where physics runs.</p>",
                "highlight": "toolbar_play",
                "wait": "play_scene",
            },
            {
                "title": "Finished!",
                "text": "<h2>You've completed the tour!</h2><p>You now know the basics of the Prima editor:</p><ul><li>Navigating the 3D Viewport</li><li>Using the Scene Hierarchy</li><li>Editing object properties</li><li>Playing your scene</li></ul><p>Explore the Tutorials panel for more in-depth lessons.</p>",
                "highlight": None,
                "wait": "next",
            },
        ],
    },
}


HIGHLIGHT_COLOR = "#ffcc00"
FOCUS_BORDER = f"2px solid {HIGHLIGHT_COLOR}"


class TourStepPopup(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setProperty("tour_popup", True)
        self.setStyleSheet("""
            QFrame[ tour_popup="true" ] {
                background: #2d2d2d;
                border: 1px solid #569cd6;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("color: #569cd6; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("color: #d4d4d4; font-size: 12px;")
        layout.addWidget(self.text_label)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar { background: #3c3c3c; border: none; border-radius: 2px; }
            QProgressBar::chunk { background: #569cd6; border-radius: 2px; }
        """)
        layout.addWidget(self.progress)

        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(6)

        self.skip_btn = QPushButton("Skip Tour")
        self.skip_btn.setFixedHeight(24)
        self.skip_btn.setStyleSheet("""
            QPushButton { background: #555; color: #ccc; border: none; padding: 2px 10px; border-radius: 3px; font-size: 11px; }
            QPushButton:hover { background: #666; }
        """)
        btn_bar.addWidget(self.skip_btn)

        btn_bar.addStretch()

        self.back_btn = QPushButton("Back")
        self.back_btn.setFixedHeight(24)
        self.back_btn.setStyleSheet("""
            QPushButton { background: #0e639c; color: white; border: none; padding: 2px 12px; border-radius: 3px; font-size: 11px; }
            QPushButton:hover { background: #1177bb; }
            QPushButton:disabled { background: #3c3c3c; color: #666; }
        """)
        btn_bar.addWidget(self.back_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedHeight(24)
        self.next_btn.setStyleSheet("""
            QPushButton { background: #0e639c; color: white; border: none; padding: 2px 16px; border-radius: 3px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background: #1177bb; }
        """)
        btn_bar.addWidget(self.next_btn)

        layout.addLayout(btn_bar)

        self.adjustSize()

    def show_step(self, step, index, total):
        self.title_label.setText(step["title"])
        self.text_label.setText(step["text"])
        self.progress.setMaximum(total)
        self.progress.setValue(index + 1)
        is_last = index == total - 1
        self.next_btn.setText("Finish" if is_last else "Next")
        self.back_btn.setEnabled(index > 0)
        self.adjustSize()


class TutorialGuide(QObject):
    def __init__(self, main_window, engine):
        super().__init__(main_window)
        self.main_window = main_window
        self.engine = engine
        self.popup = TourStepPopup(main_window.centralWidget())
        self.popup.hide()
        self.active_tour = None
        self.current_step = 0
        self._highlighted_widgets = []
        self._waiting_for = None
        self._connected_signals = []
        self._persisted_stylesheets = {}

        self.popup.next_btn.clicked.connect(self._on_next)
        self.popup.back_btn.clicked.connect(self._on_back)
        self.popup.skip_btn.clicked.connect(self._stop_tour)

    def start_tour(self, tour_key):
        if not hasattr(self.main_window, 'viewport') or not self.main_window.viewport:
            return
        if tour_key not in TOURS:
            return
        self._stop_tour()
        self.active_tour = tour_key
        self.current_step = 0
        self._show_current_step()

    def _stop_tour(self):
        self._clear_highlight()
        for obj, signal, handler in self._connected_signals:
            try:
                signal.disconnect(handler)
            except Exception:
                pass
        self._connected_signals.clear()
        self.active_tour = None
        self.current_step = 0
        self.popup.hide()
        self._waiting_for = None

    def _show_current_step(self):
        if not self.active_tour:
            return
        tour = TOURS[self.active_tour]
        steps = tour["steps"]
        if self.current_step >= len(steps):
            self._stop_tour()
            return

        step = steps[self.current_step]
        self._clear_highlight()

        self.popup.show_step(step, self.current_step, len(steps))
        self._position_popup(step.get("highlight"))
        self.popup.show()
        self.popup.raise_()

        self._apply_highlight(step.get("highlight"))
        self._setup_wait(step)

    def _position_popup(self, highlight_key):
        cw = self.main_window.centralWidget()
        target = self._widget_for_key(highlight_key)
        cw_rect = cw.rect()

        if target and target.isVisible():
            tr = target.geometry()
            local_tl = target.mapTo(cw, tr.topLeft())
            local_br = target.mapTo(cw, tr.bottomRight())
            target_rect = QRect(local_tl, local_br)
            popup_x = target_rect.center().x() - self.popup.width() // 2
            popup_y = target_rect.bottom() + 10
            if popup_y + self.popup.height() > cw_rect.bottom():
                popup_y = target_rect.top() - self.popup.height() - 10
            popup_x = max(cw_rect.left() + 10, min(popup_x, cw_rect.right() - self.popup.width() - 10))
        else:
            popup_x = cw_rect.center().x() - self.popup.width() // 2
            popup_y = cw_rect.bottom() - self.popup.height() - 40

        popup_x = max(0, popup_x)
        popup_y = max(0, popup_y)
        self.popup.move(popup_x, popup_y)

    def _widget_for_key(self, key):
        if key is None:
            return None
        mw = self.main_window
        MAP = {
            "viewport": mw.viewport,
            "hierarchy": mw.hierarchy,
            "properties": mw.properties,
            "toolbar_play": mw._play_action,
        }
        return MAP.get(key)

    def _apply_highlight(self, key):
        self._clear_highlight()
        widget = self._widget_for_key(key)
        if widget is None:
            return
        ss = widget.styleSheet()
        self._persisted_stylesheets[widget] = ss
        extra = f"border: {FOCUS_BORDER};"
        widget.setStyleSheet(ss + extra)
        self._highlighted_widgets.append(widget)
        widget.raise_()

    def _clear_highlight(self):
        for w in self._highlighted_widgets:
            old_ss = self._persisted_stylesheets.pop(w, "")
            w.setStyleSheet(old_ss)
        self._highlighted_widgets.clear()

    def _setup_wait(self, step):
        self._cleanup_wait()
        wait = step.get("wait", "next")
        self._waiting_for = wait

        if wait == "next":
            return  # button handler does it

        elif wait == "orbit":
            return  # connected to viewport.orbited

        elif wait.startswith("select:"):
            target_name = wait.split(":", 1)[1]
            handler = lambda obj, tn=target_name: self._check_selection(obj, tn)
            self.main_window.hierarchy.selection_changed.connect(handler)
            self._connected_signals.append((self.main_window.hierarchy, self.main_window.hierarchy.selection_changed, handler))

        elif wait.startswith("click:"):
            parts = wait.split(":")
            target_type = parts[1] if len(parts) > 1 else ""
            target_name = parts[2] if len(parts) > 2 else ""

        elif wait == "property_change":
            handler = lambda: self._advance()
            self.main_window.properties.property_changed.connect(handler)
            self._connected_signals.append((self.main_window.properties, self.main_window.properties.property_changed, handler))

        elif wait == "play_scene":
            handler = lambda: self._advance()
            self.main_window._play_triggered.connect(handler)
            self._connected_signals.append((self.main_window, self.main_window._play_triggered, handler))

    def _cleanup_wait(self):
        self._waiting_for = None

    def _check_selection(self, obj, target_name):
        if obj and obj.name == target_name:
            self._advance()

    def _on_viewport_orbited(self):
        if self._waiting_for == "orbit":
            self._advance()

    def _on_next(self):
        if self._waiting_for == "next":
            self._advance()

    def _on_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self._show_current_step()

    def _advance(self):
        self._cleanup_wait()
        self.current_step += 1
        self._show_current_step()
