from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout,
    QStatusBar, QTabWidget, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from prima.engine.core import Engine
from prima.engine.objects import Part, Sphere, Camera3D
from prima.engine.math_utils import Vector3

from .viewport import Viewport3D
from .hierarchy import HierarchyPanel
from .properties import PropertyPanel
from .toolbar import EditorToolbar
from .console import ConsolePanel
from .tutorial_panel import TutorialPanel


class MainWindow(QMainWindow):
    _play_triggered = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prima Engine - 3D Game Editor")
        self.setMinimumSize(1200, 750)

        self.engine = Engine()
        self._create_default_scene()

        self._setup_ui()

        from .tutorial_guide import TutorialGuide
        self.tutorial_guide = TutorialGuide(self, self.engine)
        self.tutorial_panel.set_tour_callback(self.tutorial_guide.start_tour)

        self.hierarchy.refresh()

    def _create_default_scene(self):
        ground = Part("Ground")
        ground.size = Vector3(20, 0.5, 20)
        ground.position = Vector3(0, -0.25, 0)
        ground.anchored = True
        ground.set_color(0.3, 0.6, 0.3)
        self.engine.scene.add_object(ground)

        cube = Part("Cube")
        cube.position = Vector3(0, 1.5, 0)
        cube.size = Vector3(1.5, 1.5, 1.5)
        cube.set_color(0.8, 0.3, 0.2)
        self.engine.scene.add_object(cube)

        sphere = Sphere("Sphere")
        sphere.position = Vector3(3, 1, 0)
        sphere.size = Vector3(1, 1, 1)
        sphere.set_color(0.2, 0.5, 0.8)
        self.engine.scene.add_object(sphere)

        sun = __import__("prima.engine.objects", fromlist=["Light"]).Light("Sun")
        sun.position = Vector3(20, 30, 20)
        sun.light_type = "Directional"
        sun.intensity = 1.5
        self.engine.scene.add_object(sun)

    def _setup_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        self.hierarchy = HierarchyPanel(self.engine)
        self.hierarchy.selection_changed.connect(self._on_selection_changed)
        splitter.addWidget(self.hierarchy)

        center_splitter = QSplitter(Qt.Vertical)
        self.viewport = Viewport3D(self.engine)
        self.viewport.object_selected.connect(self._on_selection_changed)
        center_splitter.addWidget(self.viewport)

        tab_widget = QTabWidget()
        self.console = ConsolePanel()
        tab_widget.addTab(self.console, "Console")
        self.tutorial_panel = TutorialPanel(engine=self.engine)
        tab_widget.addTab(self.tutorial_panel, "Tutorials")
        center_splitter.addWidget(tab_widget)
        center_splitter.setSizes([600, 200])
        splitter.addWidget(center_splitter)

        self.properties = PropertyPanel(self.engine)
        self.properties.property_changed.connect(lambda: self.viewport.update())
        splitter.addWidget(self.properties)

        splitter.setSizes([250, 700, 250])
        self.setCentralWidget(splitter)

        self._setup_toolbar()
        self.statusBar().showMessage("Ready")

    def _setup_toolbar(self):
        toolbar = EditorToolbar(self)
        self.addToolBar(toolbar)
        self._play_action = toolbar._play_action
        self._play_action.triggered.connect(self._play_triggered.emit)

    def _on_selection_changed(self, obj):
        self.properties.show_object(obj)
        if obj and hasattr(self.viewport, 'selected_object'):
            self.viewport.selected_object = obj
        self.viewport.update()

    def closeEvent(self, event):
        self.engine.shutdown()
        event.accept()
