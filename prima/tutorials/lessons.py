ENGINE_LESSONS = [
    # ── Scene & Engine ──────────────────────────────────────────
    {
        "category": "Scene & Engine",
        "title": "scene.gravity",
        "content": """
<p><b>Type:</b> <code>Vector3</code></p>
<p>Controls the direction and strength of gravity in the scene. Default is <code>(0, -9.81, 0)</code>, which pulls objects downward at Earth's gravity.</p>
<p>Set it to <code>(0, 0, 0)</code> for zero gravity (space), or change the Y value for stronger/weaker gravity.</p>
        """,
        "example": "scene.gravity = Vector3(0, -5, 0)  # Moon-like gravity\nscene.gravity = Vector3(0, 0, 0)    # Zero gravity",
        "notes": "Gravity only affects non-anchored objects."
    },
    {
        "category": "Scene & Engine",
        "title": "scene.ambient_color",
        "content": """
<p><b>Type:</b> <code>tuple(float, float, float)</code></p>
<p>Sets the ambient (background) light color of the scene. This fills in shadow areas so they aren't completely black.</p>
<p>Values are RGB from 0.0 to 1.0. Default is <code>(0.3, 0.3, 0.4)</code> (a dark blue-gray).</p>
        """,
        "example": "scene.ambient_color = (0.5, 0.5, 0.6)  # Brighter ambient\nscene.ambient_color = (0.1, 0.1, 0.2)  # Dark, moody",
        "notes": "Higher values = more light in shadowed areas."
    },
    {
        "category": "Scene & Engine",
        "title": "scene.ambient_intensity",
        "content": """
<p><b>Type:</b> <code>float</code></p>
<p>Multiplier for the ambient color. Default is <code>0.3</code>.</p>
<p>Controls how much ambient light affects the scene. Set higher for a brighter scene overall.</p>
        """,
        "example": "scene.ambient_intensity = 0.5  # Brighter shadows\nscene.ambient_intensity = 0.0  # No ambient light (pitch black shadows)",
        "notes": "Works together with <code>ambient_color</code>."
    },
    {
        "category": "Scene & Engine",
        "title": "engine.time_scale",
        "content": """
<p><b>Type:</b> <code>float</code></p>
<p>Controls the speed of time in the engine. Default is <code>1.0</code> (real-time).</p>
<p>Set to <code>2.0</code> for double speed, <code>0.5</code> for slow motion, or <code>0.0</code> to pause time-based updates.</p>
        """,
        "example": "engine.time_scale = 2.0  # Fast forward\nengine.time_scale = 0.0  # Freeze",
        "notes": "Does not affect rendering, only physics and script updates."
    },
    {
        "category": "Scene & Engine",
        "title": "engine.fps",
        "content": """
<p><b>Type:</b> <code>float</code> (read-only)</p>
<p>Displays the current frames-per-second the engine is rendering at.</p>
<p>Useful for performance monitoring. Higher FPS means smoother visuals.</p>
        """,
        "example": "print(f\"Current FPS: {engine.fps}\")",
        "notes": "Updates once per second."
    },
    {
        "category": "Scene & Engine",
        "title": "engine.delta_time",
        "content": """
<p><b>Type:</b> <code>float</code> (read-only)</p>
<p>The time in seconds since the last frame was rendered. Typically around <code>0.016</code> at 60 FPS.</p>
<p>Always use delta_time when moving objects to ensure smooth, frame-rate-independent motion.</p>
        """,
        "example": "obj.position = obj.position + Vector3(1, 0, 0) * engine.delta_time",
        "notes": "Affected by <code>time_scale</code>."
    },
    {
        "category": "Scene & Engine",
        "title": "engine.elapsed_time",
        "content": """
<p><b>Type:</b> <code>float</code> (read-only)</p>
<p>Total time in seconds since the engine started running.</p>
<p>Useful for time-based animations that need to loop or track duration.</p>
        """,
        "example": "import math\ny = math.sin(engine.elapsed_time) * 3\nobj.position = Vector3(0, y, 0)",
        "notes": "Not affected by pausing."
    },
    {
        "category": "Scene & Engine",
        "title": "engine.paused",
        "content": """
<p><b>Type:</b> <code>bool</code></p>
<p>When <code>True</code>, the engine stops updating time, physics, and scripts.</p>
<p>Useful for pause menus or editor breakpoints.</p>
        """,
        "example": "engine.paused = True   # Pause everything\nengine.paused = False  # Resume",
        "notes": "Rendering continues even when paused."
    },

    # ── Vector3 ────────────────────────────────────────────────
    {
        "category": "Vector3 Math",
        "title": "Vector3(x, y, z)",
        "content": """
<p><b>Constructor:</b> Creates a 3D vector/point.</p>
<p>Vector3 is the fundamental type for all positions, rotations, and sizes in Prima.</p>
        """,
        "example": "v = Vector3(1, 2, 3)\nprint(v.x, v.y, v.z)  # 1.0 2.0 3.0",
        "notes": "All components default to 0.0 if not provided."
    },
    {
        "category": "Vector3 Math",
        "title": "Vector3.zero(), .one(), .up(), .right(), .forward()",
        "content": """
<p><b>Static:</b> Common vector constants.</p>
<ul>
<li><code>zero()</code> - (0, 0, 0)</li>
<li><code>one()</code> - (1, 1, 1)</li>
<li><code>up()</code> - (0, 1, 0)</li>
<li><code>right()</code> - (1, 0, 0)</li>
<li><code>forward()</code> - (0, 0, -1)</li>
</ul>
        """,
        "example": "v = Vector3.up()  # Same as Vector3(0, 1, 0)",
        "notes": "Forward is -Z to match OpenGL conventions."
    },
    {
        "category": "Vector3 Math",
        "title": "v.length()",
        "content": """
<p><b>Method:</b> Returns the magnitude (length) of the vector.</p>
<p>Useful for measuring distances or normalizing vectors.</p>
        """,
        "example": "v = Vector3(3, 4, 0)\nprint(v.length())  # 5.0",
        "notes": "Also known as the Euclidean norm."
    },
    {
        "category": "Vector3 Math",
        "title": "v.normalized()",
        "content": """
<p><b>Method:</b> Returns a unit vector (length = 1) in the same direction.</p>
<p>Essential for direction calculations without magnitude.</p>
        """,
        "example": "v = Vector3(5, 0, 0)\nn = v.normalized()  # (1, 0, 0)",
        "notes": "Returns (0,0,0) if the vector length is 0."
    },
    {
        "category": "Vector3 Math",
        "title": "v.dot(other)",
        "content": """
<p><b>Method:</b> Returns the dot product of two vectors.</p>
<p>Useful for calculating angles between vectors: <code>cos(angle) = a.dot(b) / (a.length() * b.length())</code>.</p>
        """,
        "example": "a = Vector3(1, 0, 0)\nb = Vector3(0, 1, 0)\nprint(a.dot(b))  # 0.0 (perpendicular)",
        "notes": "Returns 0 for perpendicular vectors, 1 for parallel in same direction."
    },
    {
        "category": "Vector3 Math",
        "title": "v.cross(other)",
        "content": """
<p><b>Method:</b> Returns the cross product of two vectors.</p>
<p>Gives a vector perpendicular to both inputs. Used for surface normals and rotation axes.</p>
        """,
        "example": "a = Vector3(1, 0, 0)\nb = Vector3(0, 1, 0)\nc = a.cross(b)  # (0, 0, 1)",
        "notes": "Order matters! a.cross(b) = -b.cross(a)."
    },
    {
        "category": "Vector3 Math",
        "title": "Vector3.lerp(a, b, t)",
        "content": """
<p><b>Static:</b> Linearly interpolates between two vectors.</p>
<p><code>t</code> should be between 0 and 1. Returns <code>a</code> when t=0, <code>b</code> when t=1.</p>
        """,
        "example": "a = Vector3(0, 0, 0)\nb = Vector3(10, 0, 0)\nmid = Vector3.lerp(a, b, 0.5)  # (5, 0, 0)",
        "notes": "Great for smooth transitions and animations."
    },

    # ── Scene Objects ──────────────────────────────────────────
    {
        "category": "Scene Objects",
        "title": "obj.position",
        "content": """
<p><b>Type:</b> <code>Vector3</code></p>
<p>The local position of the object relative to its parent. Default is <code>(0, 0, 0)</code>.</p>
<p>Changing position moves the object in 3D space.</p>
        """,
        "example": "obj.position = Vector3(10, 5, -3)\nobj.position.y += 1",
        "notes": "Parent-relative. Use <code>get_world_position()</code> for world space."
    },
    {
        "category": "Scene Objects",
        "title": "obj.rotation",
        "content": """
<p><b>Type:</b> <code>Vector3</code> (Euler angles in radians)</p>
<p>The rotation of the object around each axis (pitch, yaw, roll).</p>
<p>Rotation order: Y (yaw) → X (pitch) → Z (roll).</p>
        """,
        "example": "import math\nobj.rotation = Vector3(math.radians(45), 0, 0)  # 45 degree tilt",
        "notes": "In the editor, rotations are displayed in degrees for convenience."
    },
    {
        "category": "Scene Objects",
        "title": "obj.size",
        "content": """
<p><b>Type:</b> <code>Vector3</code></p>
<p>The scale/size of the object. Default is <code>(1, 1, 1)</code>.</p>
<p>Setting size to <code>(2, 1, 1)</code> makes an object twice as wide on the X axis.</p>
        """,
        "example": "obj.size = Vector3(4, 0.5, 4)  # Wide and flat\nobj.size = Vector3(1, 5, 1)     # Tall and thin",
        "notes": "Cannot be negative. Minimum is 0.01."
    },
    {
        "category": "Scene Objects",
        "title": "obj.visible",
        "content": """
<p><b>Type:</b> <code>bool</code></p>
<p>Whether the object is rendered. Default is <code>True</code>.</p>
<p>Set to <code>False</code> to hide an object without deleting it.</p>
        """,
        "example": "obj.visible = False  # Hide the object",
        "notes": "Hidden objects still exist in the scene and can be found by scripts."
    },
    {
        "category": "Scene Objects",
        "title": "obj.name",
        "content": """
<p><b>Type:</b> <code>str</code></p>
<p>The name of the object. Used for identification and <code>find_by_name()</code>.</p>
<p>Names don't need to be unique, but it helps to keep them descriptive.</p>
        """,
        "example": "obj.name = \"Player Spawn Point\"\nfound = scene.find_by_name(\"Player Spawn Point\")",
        "notes": "Case-sensitive."
    },
    {
        "category": "Scene Objects",
        "title": "obj.parent / obj.children",
        "content": """
<p><b>Type:</b> <code>SceneObject</code> / <code>list</code></p>
<p>Every object can have one parent and multiple children. This forms the scene hierarchy.</p>
<p>When a parent moves, all children move with it. Children's positions are relative to their parent.</p>
        """,
        "example": "obj.set_parent(other_obj)           # Attach to parent\nchildren = obj.children               # List of children\nparent = obj.parent                   # Parent object (or None)",
        "notes": "Root object has no parent."
    },
    {
        "category": "Scene Objects",
        "title": "obj.get_world_position()",
        "content": """
<p><b>Method:</b> Returns the absolute position of the object in world space.</p>
<p>Unlike <code>position</code> which is relative to parent, this gives the actual position in the scene.</p>
        """,
        "example": "wp = obj.get_world_position()\nprint(f\"World position: {wp}\")",
        "notes": "Read-only. To set world position, calculate the local position relative to parent."
    },

    # ── Scene Physics Config ──────────────────────────────────
    {
        "category": "Scene Physics",
        "title": "scene.physics_enabled",
        "content": """
<p><b>Type:</b> <code>bool</code></p>
<p>Whether physics simulation is active in the scene. Default is <code>True</code>.</p>
<p>Set to <code>False</code> to freeze all physics (objects stop moving, collisions stop).</p>
        """,
        "example": "scene.physics_enabled = False  # Freeze all physics\nscene.physics_enabled = True   # Re-enable physics",
        "notes": "Objects keep their current velocities when disabled, and resume when re-enabled."
    },
    {
        "category": "Scene Physics",
        "title": "scene.solver_iterations",
        "content": """
<p><b>Type:</b> <code>int</code> (1-64, default: 8)</p>
<p>Number of constraint solver iterations per physics step. More iterations = more stable contacts, but slower.</p>
<p>Simple scenes with few stacked objects work fine at 4-6. For complex stacks or chains, use 10-20.</p>
        """,
        "example": "scene.solver_iterations = 4   # Faster, less stable\nscene.solver_iterations = 16  # More stable stacks",
        "notes": "Each iteration adds CPU cost. Find the minimum needed for your scene."
    },
    {
        "category": "Scene Physics",
        "title": "scene.linear_damping",
        "content": """
<p><b>Type:</b> <code>float</code> (0.0-1.0, default: 0.01)</p>
<p>Velocity damping applied each frame. 0.0 = no damping (objects never slow down), 1.0 = instant stop.</p>
<p>A small amount (0.01) helps objects settle faster. For space scenes, use 0.0.</p>
        """,
        "example": "scene.linear_damping = 0.0   # No damping (space)\nscene.linear_damping = 0.05  # Thick atmosphere",
        "notes": "Applied as multiplicative factor: vel *= (1 - damping) each frame."
    },
    {
        "category": "Scene Physics",
        "title": "scene.angular_damping",
        "content": """
<p><b>Type:</b> <code>float</code> (0.0-1.0, default: 0.01)</p>
<p>Angular velocity damping applied each frame. Controls how quickly spinning objects slow down.</p>
<p>Same as linear damping but for rotation. Higher values = faster spin decay.</p>
        """,
        "example": "scene.angular_damping = 0.0   # Objects spin forever\nscene.angular_damping = 0.1   # Quick spin decay",
        "notes": "Only affects non-anchored objects with velocity."
    },
    {
        "category": "Scene Physics",
        "title": "obj.physics_material",
        "content": """
<p><b>Type:</b> <code>str</code></p>
<p>The physics material preset name. Controls restitution (bounciness) and friction.</p>
<p>Available: Concrete, Wood, Metal, Rubber, Plastic, Stone, Glass, Ice, Carpet, Default.</p>
<p>Each preset has different restitution, friction, and density values. Density affects auto-computed mass.</p>
        """,
        "example": "obj.physics_material = \"Rubber\"  # Bouncy!\nobj.physics_material = \"Ice\"     # Slippery\nobj.physics_material = \"Metal\"   # Heavy, hard",
        "notes": "Changing material auto-computes mass = density x volume in the editor."
    },
    {
        "category": "Scene Physics",
        "title": "scene.default_restitution",
        "content": """
<p><b>Type:</b> <code>float</code> (0.0-1.0, default: 0.3)</p>
<p>Default bounciness for objects that don't have a physics material assigned.</p>
<p>0.0 = no bounce (clay), 1.0 = perfect bounce (superball).</p>
        """,
        "example": "scene.default_restitution = 0.0   # No bounce\nscene.default_restitution = 0.8   # Very bouncy",
        "notes": "Per-object physics material overrides this default."
    },
    {
        "category": "Scene Physics",
        "title": "scene.default_friction",
        "content": """
<p><b>Type:</b> <code>float</code> (0.0-10.0, default: 0.5)</p>
<p>Default friction coefficient for objects without a physics material.</p>
<p>0.0 = frictionless (ice), 1.0+ = high friction (rubber, carpet).</p>
        """,
        "example": "scene.default_friction = 0.0   # Slippery surface\nscene.default_friction = 2.0   # Sticky surface",
        "notes": "Friction is applied tangential to the contact surface."
    },

    # ── Parts & Physics ────────────────────────────────────────
    {
        "category": "Parts & Physics",
        "title": "part.anchored",
        "content": """
<p><b>Type:</b> <code>bool</code></p>
<p>When <code>True</code>, the part is fixed in place and not affected by gravity or physics.</p>
<p>Walls, floors, and static objects should be anchored. Moveable objects like players and projectiles should not.</p>
        """,
        "example": "part.anchored = True    # Won't move\npart.anchored = False   # Affected by gravity",
        "notes": "Anchored objects are simulated as having infinite mass."
    },
    {
        "category": "Parts & Physics",
        "title": "part.can_collide",
        "content": """
<p><b>Type:</b> <code>bool</code></p>
<p>Whether the part can collide with other objects. Default is <code>True</code>.</p>
<p>Set to <code>False</code> to make objects pass through each other (like triggers or visual effects).</p>
        """,
        "example": "part.can_collide = False  # Objects can pass through",
        "notes": "Currently reserved for future physics system."
    },
    {
        "category": "Parts & Physics",
        "title": "part.mass",
        "content": """
<p><b>Type:</b> <code>float</code></p>
<p>The mass of the part in arbitrary units. Default is <code>1.0</code>.</p>
<p>Heavier objects are harder to push. Mass affects gravity force (<code>F = m * g</code>).</p>
        """,
        "example": "part.mass = 10.0  # Heavy\npart.mass = 0.1   # Light",
        "notes": "Only matters for non-anchored objects."
    },
    {
        "category": "Parts & Physics",
        "title": "part.velocity",
        "content": """
<p><b>Type:</b> <code>Vector3</code></p>
<p>The current velocity of the part in units/second. Automatically updated by physics.</p>
<p>Set initial velocity for launching objects (projectiles, jumping).</p>
        """,
        "example": "part.velocity = Vector3(10, 5, 0)  # Launch diagonally",
        "notes": "Automatically affected by gravity each frame."
    },
    {
        "category": "Parts & Physics",
        "title": "part.color",
        "content": """
<p><b>Type:</b> <code>tuple(float, float, float)</code></p>
<p>The RGB color of the part, values 0.0 to 1.0 each.</p>
<p>Also accessible via <code>part.material.color</code>.</p>
        """,
        "example": "part.color = (1.0, 0.2, 0.2)  # Reddish\npart.set_color(0.2, 0.5, 1.0)  # Blue (uses 0-255 internally)",
        "notes": "Changing color also updates the material."
    },

    # ── Camera ─────────────────────────────────────────────────
    {
        "category": "Camera",
        "title": "camera.field_of_view",
        "content": """
<p><b>Type:</b> <code>float</code></p>
<p>The vertical field of view in degrees. Default is <code>70.0</code>.</p>
<p>Lower values = zoomed in (like a telescope). Higher values = wide angle (can cause distortion).</p>
        """,
        "example": "cam.field_of_view = 90.0  # Wide angle\ncam.field_of_view = 30.0  # Zoomed in",
        "notes": "Typical range: 40-110 degrees."
    },
    {
        "category": "Camera",
        "title": "camera.near_plane / camera.far_plane",
        "content": """
<p><b>Type:</b> <code>float</code></p>
<p>The near and far clipping planes. Objects closer than <code>near</code> or farther than <code>far</code> are not rendered.</p>
<p>Default: near=0.01, far=1000.0.</p>
        """,
        "example": "cam.near_plane = 0.1\ncam.far_plane = 5000.0  # See farther",
        "notes": "Very large far/near ratios can cause z-fighting (rendering artifacts)."
    },

    # ── Lights ─────────────────────────────────────────────────
    {
        "category": "Lights",
        "title": "light.light_type",
        "content": """
<p><b>Type:</b> <code>str</code></p>
<p>The type of light: <code>"Directional"</code>, <code>"Point"</code>, or <code>"Spot"</code>.</p>
<ul>
<li><b>Directional:</b> Sun-like light that shines evenly from one direction.</li>
<li><b>Point:</b> Light that radiates from a single position.</li>
<li><b>Spot:</b> A cone-shaped light (like a flashlight).</li>
</ul>
        """,
        "example": "light.light_type = \"Point\"\nlight.light_type = \"Directional\"",
        "notes": "Currently all types render the same. Type affects future features."
    },
    {
        "category": "Lights",
        "title": "light.intensity",
        "content": """
<p><b>Type:</b> <code>float</code></p>
<p>The brightness of the light. Default is <code>1.0</code>.</p>
<p>Higher values = brighter light.</p>
        """,
        "example": "light.intensity = 2.0   # Very bright\nlight.intensity = 0.2   # Dim",
        "notes": "Works together with <code>light.color</code>."
    },
    {
        "category": "Lights",
        "title": "light.range",
        "content": """
<p><b>Type:</b> <code>float</code></p>
<p>The maximum distance the light affects objects. Default is <code>50.0</code>.</p>
<p>Only relevant for Point and Spot lights.</p>
        """,
        "example": "light.range = 100.0  # Shines far",
        "notes": "Directional lights are not affected by range."
    },

    # ── Materials ──────────────────────────────────────────────
    {
        "category": "Materials",
        "title": "material.color",
        "content": """
<p><b>Type:</b> <code>QColor</code></p>
<p>The base color of the material. Affects how the object looks under light.</p>
<p>Can be set with RGB values (0-255) or using <code>set_color()</code>.</p>
        """,
        "example": "from PyQt5.QtGui import QColor\nmat.color = QColor(255, 50, 50)  # Red\nmat.set_color(50, 255, 50)       # Green (r, g, b 0-255)",
        "notes": "Also accessible via <code>part.color</code> as normalized float tuple."
    },
    {
        "category": "Materials",
        "title": "material.transparency",
        "content": """
<p><b>Type:</b> <code>float</code> (0.0 to 1.0)</p>
<p>How transparent the material is. 0.0 = fully opaque, 1.0 = fully invisible.</p>
        """,
        "example": "mat.transparency = 0.5  # See-through\nmat.transparency = 0.0  # Solid",
        "notes": "Does not affect lighting calculations."
    },
]
