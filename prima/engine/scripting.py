import types


class ScriptContext:
    def __init__(self, engine):
        self.engine = engine
        self.game = engine
        self.scene = engine.scene
        self._scripts = {}

    def create_script(self, source, obj=None):
        namespace = {
            "engine": self.engine,
            "scene": self.scene,
            "game": self.engine,
            "object": obj,
            "print": print,
            "Vector3": __import__("prima.engine.math_utils", fromlist=["Vector3"]).Vector3,
        }

        try:
            exec(compile(source, "<script>", "exec"), namespace)
        except Exception as e:
            print(f"[Script Error] {e}")

        return namespace

    def run_script(self, source, obj=None):
        return self.create_script(source, obj)
