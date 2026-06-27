from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from prima.engine.objects import Part, Wedge, Cylinder, Sphere, Camera3D, Light, Script
from prima.engine.scene import SceneObject


class HierarchyPanel(QTreeWidget):
    selection_changed = pyqtSignal(object)

    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setHeaderLabel("Scene Hierarchy")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemClicked.connect(self._on_item_clicked)
        self._updating = False

    def refresh(self):
        self._updating = True
        self.clear()
        root = self.engine.scene.root
        item = QTreeWidgetItem(self, [root.name])
        item.setData(0, Qt.UserRole, root.id)
        self._populate_children(root, item)
        self.expandAll()
        self._updating = False

    def _populate_children(self, obj, parent_item):
        for child in obj.children:
            item = QTreeWidgetItem(parent_item, [child.name])
            item.setData(0, Qt.UserRole, child.id)
            self._populate_children(child, item)

    def _on_item_clicked(self, item, col):
        if self._updating:
            return
        obj_id = item.data(0, Qt.UserRole)
        obj = self.engine.scene.find_by_id(obj_id)
        if obj:
            self.selection_changed.emit(obj)

    def _show_context_menu(self, pos):
        item = self.itemAt(pos)
        menu = QMenu()

        add_menu = menu.addMenu("Add Object")
        add_menu.addAction("Part (Box)").triggered.connect(lambda: self._add_object("Part"))
        add_menu.addAction("Sphere").triggered.connect(lambda: self._add_object("Sphere"))
        add_menu.addAction("Wedge").triggered.connect(lambda: self._add_object("Wedge"))
        add_menu.addAction("Cylinder").triggered.connect(lambda: self._add_object("Cylinder"))
        add_menu.addSeparator()
        add_menu.addAction("Camera").triggered.connect(lambda: self._add_object("Camera"))
        add_menu.addAction("Light").triggered.connect(lambda: self._add_object("Light"))
        add_menu.addAction("Script").triggered.connect(lambda: self._add_object("Script"))

        if item:
            parent_obj = None
            obj_id = item.data(0, Qt.UserRole)
            parent_obj = self.engine.scene.find_by_id(obj_id)

            menu.addSeparator()
            dup = menu.addAction("Duplicate")
            dup.triggered.connect(lambda: self._duplicate_object(parent_obj))
            menu.addAction("Delete").triggered.connect(lambda: self._delete_object(parent_obj))

        menu.exec_(self.viewport().mapToGlobal(pos))

    def _add_object(self, obj_type):
        sel = self.selectedItems()
        parent = self.engine.scene.root
        if sel:
            pid = sel[0].data(0, Qt.UserRole)
            p = self.engine.scene.find_by_id(pid)
            if p:
                parent = p

        cls_map = {
            "Part": Part, "Sphere": Sphere, "Wedge": Wedge,
            "Cylinder": Cylinder, "Camera": Camera3D,
            "Light": Light, "Script": Script,
        }
        obj = cls_map.get(obj_type, SceneObject)(f"{obj_type}_{len(parent.children)}")
        self.engine.scene.add_object(obj, parent)
        self.refresh()

    def _delete_object(self, obj):
        if obj and obj.object_type != "Root":
            self.engine.scene.remove_object(obj)
            self.refresh()

    def _duplicate_object(self, obj):
        if obj and obj.object_type != "Root":
            dup = obj.duplicate()
            self.engine.scene.add_object(dup, obj.parent)
            self.refresh()
