# Example Cython user script
# Compile: python scripts/setup.py build_ext --inplace
# Cython compiles this to native code - just add type annotations!

from prima.engine.math_utils import Vector3


def init():
    print("Script initialized (Cython compiled!)")


def update(float dt, obj):
    """Called every frame. dt in seconds, obj is the attached SceneObject."""
    if obj is None:
        return
    
    pos = obj.position
    cdef float speed = 2.0
    
    # Simple bobbing motion
    pos.y += speed * dt
    
    # Keep within bounds
    if pos.y > 5.0:
        pos.y = 0.0
    
    obj.position = pos
    obj.rotation.y += dt * 0.5
