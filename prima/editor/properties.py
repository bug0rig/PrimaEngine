from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox,
    QLabel, QPushButton, QCheckBox, QComboBox, QColorDialog,
    QScrollArea, QGroupBox, QLineEdit, QTextEdit, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from prima.engine.math_utils import Vector3
from prima.engine.materials import PHYSICS_MATERIALS, PHYSICS_MATERIAL_NAMES


def _make_spinbox(value, min_v=-9999, max_v=9999, step=0.1, decimals=3):
    sb = QDoubleSpinBox()
    sb.setRange(min_v, max_v)
    sb.setSingleStep(step)
    sb.setDecimals(decimals)
    sb.setValue(value)
    return sb


class PropertyPanel(QScrollArea):
    property_changed = pyqtSignal()

    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.current_obj = None
        self._widgets = {}
        self.setWidgetResizable(True)
        self.setMinimumWidth(200)

        self.inner = QWidget()
        self.layout = QVBoxLayout(self.inner)
        self.setWidget(self.inner)

        self._no_selection_label = QLabel("<i>No object selected</i>")
        self._no_selection_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self._no_selection_label)

    def show_object(self, obj):
        self.current_obj = obj
        self._clear()
        if obj is None:
            self.layout.addWidget(self._no_selection_label)
            return

        header = QLabel(f"<b>{obj.object_type}: {obj.name}</b>")
        self.layout.addWidget(header)
        self._build_name(obj)
        self._build_transform(obj)
        self._build_material(obj)
        if hasattr(obj, 'anchored'):
            self._build_physics(obj)
        if obj.object_type == "Camera":
            self._build_camera(obj)
        if obj.object_type == "Light":
            self._build_light(obj)
        if obj.object_type == "Root":
            self._build_scene_settings(obj)
        if obj.object_type == "Script":
            self._build_script(obj)
        self.layout.addStretch()

    def _clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w and w is not self._no_selection_label:
                w.deleteLater()

    def _build_name(self, obj):
        group = QGroupBox("Identity")
        fl = QFormLayout(group)
        name_edit = QLineEdit(obj.name)
        name_edit.textChanged.connect(lambda t: self._set_attr(obj, 'name', t))
        fl.addRow("Name:", name_edit)
        self.layout.addWidget(group)

    def _build_transform(self, obj):
        group = QGroupBox("Transform")
        fl = QFormLayout(group)

        pos = obj.position
        sb_x = _make_spinbox(pos.x)
        sb_y = _make_spinbox(pos.y)
        sb_z = _make_spinbox(pos.z)
        sb_x.valueChanged.connect(lambda v: self._set_pos(obj, 'x', v))
        sb_y.valueChanged.connect(lambda v: self._set_pos(obj, 'y', v))
        sb_z.valueChanged.connect(lambda v: self._set_pos(obj, 'z', v))
        fl.addRow("Position:", _make_hbox(sb_x, sb_y, sb_z))

        rot = obj.rotation
        rr_x = _make_spinbox(rot.x, -360, 360, 1, 1)
        rr_y = _make_spinbox(rot.y, -360, 360, 1, 1)
        rr_z = _make_spinbox(rot.z, -360, 360, 1, 1)
        rr_x.valueChanged.connect(lambda v: self._set_rot(obj, 'x', v))
        rr_y.valueChanged.connect(lambda v: self._set_rot(obj, 'y', v))
        rr_z.valueChanged.connect(lambda v: self._set_rot(obj, 'z', v))
        fl.addRow("Rotation:", _make_hbox(rr_x, rr_y, rr_z))

        sz = obj.size
        ss_x = _make_spinbox(sz.x, 0.01, 9999)
        ss_y = _make_spinbox(sz.y, 0.01, 9999)
        ss_z = _make_spinbox(sz.z, 0.01, 9999)
        ss_x.valueChanged.connect(lambda v: self._set_size(obj, 'x', v))
        ss_y.valueChanged.connect(lambda v: self._set_size(obj, 'y', v))
        ss_z.valueChanged.connect(lambda v: self._set_size(obj, 'z', v))
        fl.addRow("Size:", _make_hbox(ss_x, ss_y, ss_z))

        self.layout.addWidget(group)

    def _build_material(self, obj):
        group = QGroupBox("Material")
        fl = QFormLayout(group)

        mat = getattr(obj, 'material', None)
        if mat:
            btn = QPushButton("Change Color")
            c = mat.color
            btn.setStyleSheet(f"background-color: rgb({c.red()},{c.green()},{c.blue()})")
            def pick_color():
                color = QColorDialog.getColor(mat.color)
                if color.isValid():
                    mat.color = color
                    btn.setStyleSheet(f"background-color: rgb({color.red()},{color.green()},{color.blue()})")
                    self.property_changed.emit()
            btn.clicked.connect(pick_color)
            fl.addRow("Color:", btn)

            alpha = _make_spinbox(mat.transparency, 0, 1, 0.05, 2)
            alpha.valueChanged.connect(lambda v: self._set_attr(mat, 'transparency', v))
            fl.addRow("Transparency:", alpha)

        self.layout.addWidget(group)

    def _build_physics(self, obj):
        group = QGroupBox("Physics")
        fl = QFormLayout(group)

        anchored = QCheckBox()
        anchored.setChecked(getattr(obj, 'anchored', False))
        anchored.toggled.connect(lambda v: self._set_attr(obj, 'anchored', v))
        fl.addRow("Anchored:", anchored)

        can_collide = QCheckBox()
        can_collide.setChecked(getattr(obj, 'can_collide', True))
        can_collide.toggled.connect(lambda v: self._set_attr(obj, 'can_collide', v))
        fl.addRow("Can Collide:", can_collide)

        mat_combo = QComboBox()
        mat_combo.addItems(PHYSICS_MATERIAL_NAMES)
        current_mat = getattr(obj, 'physics_material', 'Default')
        if current_mat not in PHYSICS_MATERIAL_NAMES:
            current_mat = 'Default'
        mat_combo.setCurrentText(current_mat)
        def on_mat_change(text):
            self._set_attr(obj, 'physics_material', text)
            pm = PHYSICS_MATERIALS.get(text, PHYSICS_MATERIALS['Default'])
            # Auto-set mass from density * approximate volume
            sz = obj.size
            vol = sz.x * sz.y * sz.z
            self._set_attr(obj, 'mass', max(vol * pm['density'], 0.01))
        mat_combo.currentTextChanged.connect(on_mat_change)
        fl.addRow("Material:", mat_combo)

        mass = _make_spinbox(getattr(obj, 'mass', 1.0), 0.01, 99999)
        mass.valueChanged.connect(lambda v: self._set_attr(obj, 'mass', v))
        fl.addRow("Mass:", mass)

        self.layout.addWidget(group)

    def _build_scene_settings(self, obj):
        scene = self.engine.scene

        group = QGroupBox("Scene Physics")
        fl = QFormLayout(group)

        enabled = QCheckBox()
        enabled.setChecked(getattr(scene, 'physics_enabled', True))
        enabled.toggled.connect(lambda v: self._set_scene_attr('physics_enabled', v))
        fl.addRow("Enabled:", enabled)

        gx = _make_spinbox(scene.gravity.x, -100, 100, 0.1, 2)
        gy = _make_spinbox(scene.gravity.y, -100, 100, 0.1, 2)
        gz = _make_spinbox(scene.gravity.z, -100, 100, 0.1, 2)
        gx.valueChanged.connect(lambda v: self._set_scene_gravity('x', v))
        gy.valueChanged.connect(lambda v: self._set_scene_gravity('y', v))
        gz.valueChanged.connect(lambda v: self._set_scene_gravity('z', v))
        fl.addRow("Gravity:", _make_hbox(gx, gy, gz))

        iters = QSpinBox()
        iters.setRange(1, 64)
        iters.setValue(getattr(scene, 'solver_iterations', 8))
        iters.valueChanged.connect(lambda v: self._set_scene_attr('solver_iterations', v))
        fl.addRow("Solver Iters:", iters)

        rest = _make_spinbox(getattr(scene, 'default_restitution', 0.3), 0, 1, 0.05, 2)
        rest.valueChanged.connect(lambda v: self._set_scene_attr('default_restitution', v))
        fl.addRow("Restitution:", rest)

        fric = _make_spinbox(getattr(scene, 'default_friction', 0.5), 0, 10, 0.1, 2)
        fric.valueChanged.connect(lambda v: self._set_scene_attr('default_friction', v))
        fl.addRow("Friction:", fric)

        ld = _make_spinbox(getattr(scene, 'linear_damping', 0.01), 0, 1, 0.01, 3)
        ld.valueChanged.connect(lambda v: self._set_scene_attr('linear_damping', v))
        fl.addRow("Lin Damping:", ld)

        ad = _make_spinbox(getattr(scene, 'angular_damping', 0.01), 0, 1, 0.01, 3)
        ad.valueChanged.connect(lambda v: self._set_scene_attr('angular_damping', v))
        fl.addRow("Ang Damping:", ad)

        self.layout.addWidget(group)

    def _set_scene_attr(self, attr, value):
        setattr(self.engine.scene, attr, value)
        self.property_changed.emit()

    def _set_scene_gravity(self, axis, value):
        g = self.engine.scene.gravity
        setattr(g, axis, value)
        self.engine.scene.gravity = g
        self.property_changed.emit()

    def _build_camera(self, obj):
        group = QGroupBox("Camera Settings")
        fl = QFormLayout(group)

        fov = _make_spinbox(obj.field_of_view, 1, 179, 1, 1)
        fov.valueChanged.connect(lambda v: self._set_attr(obj, 'field_of_view', v))
        fl.addRow("FOV:", fov)

        near_p = _make_spinbox(obj.near_plane, 0.001, 10, 0.1, 3)
        near_p.valueChanged.connect(lambda v: self._set_attr(obj, 'near_plane', v))
        fl.addRow("Near:", near_p)

        far_p = _make_spinbox(obj.far_plane, 1, 10000, 10, 1)
        far_p.valueChanged.connect(lambda v: self._set_attr(obj, 'far_plane', v))
        fl.addRow("Far:", far_p)

        self.layout.addWidget(group)

    def _build_light(self, obj):
        group = QGroupBox("Light Settings")
        fl = QFormLayout(group)

        lt = QComboBox()
        lt.addItems(["Directional", "Point", "Spot"])
        lt.setCurrentText(obj.light_type)
        lt.currentTextChanged.connect(lambda v: self._set_attr(obj, 'light_type', v))
        fl.addRow("Type:", lt)

        intensity = _make_spinbox(obj.intensity, 0, 100)
        intensity.valueChanged.connect(lambda v: self._set_attr(obj, 'intensity', v))
        fl.addRow("Intensity:", intensity)

        range_v = _make_spinbox(obj.range, 0, 9999)
        range_v.valueChanged.connect(lambda v: self._set_attr(obj, 'range', v))
        fl.addRow("Range:", range_v)

        self.layout.addWidget(group)

    def _build_script(self, obj):
        group = QGroupBox("Script")
        fl = QFormLayout(group)

        enabled = QCheckBox()
        enabled.setChecked(getattr(obj, 'enabled', True))
        enabled.toggled.connect(lambda v: self._set_attr(obj, 'enabled', v))
        fl.addRow("Enabled:", enabled)

        editor = QTextEdit()
        editor.setPlainText(getattr(obj, 'source', ''))
        editor.setMinimumHeight(200)
        editor.textChanged.connect(lambda: self._set_attr(obj, 'source', editor.toPlainText()))
        self.layout.addWidget(editor)

        self.layout.addWidget(group)

    def _set_attr(self, obj, attr, value):
        setattr(obj, attr, value)
        self.property_changed.emit()

    def _set_pos(self, obj, axis, value):
        p = obj.position
        setattr(p, axis, value)
        obj.position = p
        self.property_changed.emit()

    def _set_rot(self, obj, axis, value):
        r = obj.rotation
        setattr(r, axis, math.radians(value) if axis in ('x', 'y', 'z') else value)
        obj.rotation = r
        self.property_changed.emit()

    def _set_size(self, obj, axis, value):
        s = obj.size
        setattr(s, axis, value)
        obj.size = s
        self.property_changed.emit()


def _make_hbox(*widgets):
    from PyQt5.QtWidgets import QHBoxLayout, QWidget
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    for wi in widgets:
        l.addWidget(wi)
    return w


import math
