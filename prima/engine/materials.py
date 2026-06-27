from PyQt5.QtGui import QColor


PHYSICS_MATERIALS = {
    "Concrete": {"restitution": 0.05, "friction": 0.7, "density": 2400},
    "Wood":     {"restitution": 0.2,  "friction": 0.5, "density": 700},
    "Metal":    {"restitution": 0.1,  "friction": 0.4, "density": 7800},
    "Rubber":   {"restitution": 0.9,  "friction": 1.2, "density": 1200},
    "Plastic":  {"restitution": 0.4,  "friction": 0.3, "density": 950},
    "Stone":    {"restitution": 0.05, "friction": 0.8, "density": 2000},
    "Glass":    {"restitution": 0.3,  "friction": 0.2, "density": 2500},
    "Ice":      {"restitution": 0.1,  "friction": 0.05, "density": 900},
    "Carpet":   {"restitution": 0.1,  "friction": 1.5, "density": 400},
    "Default":  {"restitution": 0.3,  "friction": 0.5, "density": 1000},
}
PHYSICS_MATERIAL_NAMES = sorted(PHYSICS_MATERIALS.keys())


class Material:
    def __init__(self, name="Material"):
        self.name = name
        self.color = QColor(200, 200, 200)
        self.metallic = 0.0
        self.roughness = 0.5
        self.emissive = QColor(0, 0, 0)
        self.emissive_intensity = 0.0
        self.transparency = 1.0
        self.texture_path = None
        self.texture_id = None

    def set_color(self, r, g, b):
        self.color = QColor(r, g, b)

    def to_dict(self):
        c = self.color
        e = self.emissive
        return {
            "name": self.name,
            "color": (c.red(), c.green(), c.blue()),
            "metallic": self.metallic,
            "roughness": self.roughness,
            "emissive": (e.red(), e.green(), e.blue()),
            "emissive_intensity": self.emissive_intensity,
            "transparency": self.transparency,
            "texture_path": self.texture_path,
        }

    @staticmethod
    def from_dict(d):
        mat = Material(d.get("name", "Material"))
        c = d.get("color", (200, 200, 200))
        mat.color = QColor(*c)
        mat.metallic = d.get("metallic", 0.0)
        mat.roughness = d.get("roughness", 0.5)
        e = d.get("emissive", (0, 0, 0))
        mat.emissive = QColor(*e)
        mat.emissive_intensity = d.get("emissive_intensity", 0.0)
        mat.transparency = d.get("transparency", 1.0)
        mat.texture_path = d.get("texture_path")
        return mat

    @staticmethod
    def red():
        mat = Material("Red")
        mat.color = QColor(255, 50, 50)
        return mat

    @staticmethod
    def green():
        mat = Material("Green")
        mat.color = QColor(50, 255, 50)
        return mat

    @staticmethod
    def blue():
        mat = Material("Blue")
        mat.color = QColor(50, 50, 255)
        return mat

    @staticmethod
    def white():
        mat = Material("White")
        mat.color = QColor(255, 255, 255)
        return mat

    @staticmethod
    def gray():
        mat = Material("Gray")
        mat.color = QColor(128, 128, 128)
        return mat

    @staticmethod
    def black():
        mat = Material("Black")
        mat.color = QColor(20, 20, 20)
        return mat

    @staticmethod
    def yellow():
        mat = Material("Yellow")
        mat.color = QColor(255, 255, 50)
        return mat
