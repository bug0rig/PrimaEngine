THEME_TUTORIALS = [
    {
        "title": "Getting Started with Prima",
        "description": "Learn the basics of the Prima Engine: navigation, creating objects, and running your first scene.",
        "overview": "This tutorial covers everything you need to start building 3D worlds in Prima. You'll learn the editor layout, how to navigate the 3D viewport, create and manipulate objects, and save your work.",
        "steps": [
            {
                "title": "Editor Overview",
                "content": """
<p>The Prima Editor is divided into four main areas:</p>
<ul>
<li><b>3D Viewport</b> (center) - The main 3D scene view where you can navigate and interact with objects.</li>
<li><b>Scene Hierarchy</b> (left) - A tree view of all objects in your scene. Click to select, right-click to add/delete.</li>
<li><b>Properties Panel</b> (right) - Edit the properties of the selected object: position, rotation, size, material, and more.</li>
<li><b>Console</b> (bottom) - Type commands and see output messages.</li>
</ul>
<p>At the top, the toolbar gives you quick access to save, load, play, and camera controls.</p>
                """,
                "tip": "You can resize panels by dragging the borders between them."
            },
            {
                "title": "3D Viewport Navigation",
                "content": """
<p>Navigating the 3D viewport is intuitive:</p>
<ul>
<li><b>Orbit</b> - Hold <b>Right Mouse Button</b> and drag to orbit around the scene.</li>
<li><b>Pan</b> - Hold <b>Middle Mouse Button</b> (scroll wheel) and drag to pan.</li>
<li><b>Zoom</b> - Use the <b>Scroll Wheel</b> to zoom in and out.</li>
<li><b>Focus</b> - Press <b>F</b> to reset the camera, or select an object and press <b>Shift+F</b> to focus on it.</li>
</ul>
<p>The camera orbits around the world origin by default. When you focus on an object, the camera moves to look at it directly.</p>
                """,
                "tip": "Use the middle mouse button to quickly reposition your view without changing the orbit center."
            },
            {
                "title": "Creating Objects",
                "content": """
<p>Objects are the building blocks of your Prima world. To create one:</p>
<ol>
<li>Right-click in the <b>Scene Hierarchy</b> panel.</li>
<li>Select <b>Add Object</b> and choose a type:</li>
<ul>
<li><b>Part</b> - A box/cube, the most common building block.</li>
<li><b>Sphere</b> - A rounded object useful for balls, planets, etc.</li>
<li><b>Wedge</b> - A triangular shape for ramps and slopes.</li>
<li><b>Cylinder</b> - A cylindrical shape for pipes, columns, etc.</li>
<li><b>Camera</b> - A camera object for defining viewpoints.</li>
<li><b>Light</b> - A light source to illuminate your scene.</li>
<li><b>Script</b> - Attach Python code to objects for interactivity.</li>
</ul>
</ol>
<p>New objects appear at the world origin (0,0,0). You can then move them using the Properties panel.</p>
                """,
                "tip": "Objects are parented to whatever is selected in the hierarchy. To add at the root, make sure nothing is selected."
            },
            {
                "title": "Manipulating Objects",
                "content": """
<p>Every object has three main transform properties:</p>
<ul>
<li><b>Position</b> (X, Y, Z) - Where the object is in 3D space.</li>
<li><b>Rotation</b> (X, Y, Z) - How the object is oriented (in degrees).</li>
<li><b>Size</b> (X, Y, Z) - How large the object is.</li>
</ul>
<p>To edit these:</p>
<ol>
<li>Click on an object in the Scene Hierarchy to select it.</li>
<li>Look at the <b>Properties Panel</b> on the right.</li>
<li>Change any value by clicking in the number field and typing, or using the up/down arrows.</li>
</ol>
<p>You can also change the object's material color in the Properties panel under "Material".</p>
                """,
                "tip": "Hold Shift while dragging a spinbox arrow to change values faster."
            },
            {
                "title": "Saving and Loading",
                "content": """
<p>Your scenes can be saved and loaded as <code>.prima</code> files:</p>
<ul>
<li><b>Save</b> - Click the Save button in the toolbar, or press <b>Ctrl+S</b>.</li>
<li><b>Load</b> - Click the Load button, or press <b>Ctrl+O</b>.</li>
<li><b>New</b> - Click New Scene (<b>Ctrl+N</b>) to start fresh.</li>
</ul>
<p>.prima files are JSON-based, so you can open them in any text editor to inspect or modify the data directly.</p>
                """,
                "tip": "Save often! Prima scenes are human-readable JSON - great for learning."
            },
        ]
    },
    {
        "title": "Building a 3D World",
        "description": "Learn how to create environments, use lighting, and organize your scene.",
        "overview": "This tutorial walks through building a complete 3D environment with a ground plane, buildings, lighting, and decorative objects. You'll learn scene organization and basic world-building techniques.",
        "steps": [
            {
                "title": "Creating a Ground Plane",
                "content": """
<p>A ground plane gives your world a floor to stand on:</p>
<ol>
<li>Create a new <b>Part</b> from the context menu.</li>
<li>In Properties, set <b>Size</b> to <code>X: 50, Y: 1, Z: 50</code>.</li>
<li>Set <b>Position</b> to <code>X: 0, Y: -0.5, Z: 0</code> (so the top is at Y=0).</li>
<li>Change the color to a nice green or gray in the Material section.</li>
<li>Enable <b>Anchored</b> so it doesn't fall.</li>
</ol>
<p>This creates a large flat surface. The grid in the viewport shows you where the ground is.</p>
                """,
                "tip": "Set Y to -half the height to place the surface exactly at Y=0."
            },
            {
                "title": "Building Structures",
                "content": """
<p>Use multiple parts to create buildings:</p>
<ol>
<li>Create a Part, set Size to <code>X: 4, Y: 6, Z: 4</code>, Position to <code>X: 0, Y: 3, Z: 0</code>.</li>
<li>This is your first building. Give it a warm color.</li>
<li>Create a second Part, set Size to <code>X: 5, Y: 8, Z: 5</code>, Position to <code>X: 12, Y: 4, Z: 5</code>.</li>
<li>Create a Wedge for a roof: set Size to <code>X: 5, Y: 3, Z: 5</code>, Position to <code>X: 12, Y: 8, Z: 5</code>.</li>
<li>Color the roof red or brown.</li>
</ol>
<p>For more complex shapes, combine multiple parts and parent them together.</p>
                """,
                "tip": "Parent objects to an empty 'Folder' object (just create a generic object) to keep your hierarchy organized."
            },
            {
                "title": "Adding Lighting",
                "content": """
<p>Good lighting makes your world look alive:</p>
<ol>
<li>Create a <b>Light</b> from the context menu.</li>
<li>Set its <b>Type</b> to "Directional" for a sun-like light.</li>
<li>Set <b>Position</b> to <code>X: 20, Y: 30, Z: 20</code> (high up, angled).</li>
<li>Set <b>Intensity</b> to <code>1.5</code> for bright sunlight.</li>
</ol>
<p>Directional lights shine evenly across the entire scene. For localized lighting, use "Point" lights.</p>
<p>The ambient light setting affects how dark the shadows are. You can adjust it in the scene settings.</p>
                """,
                "tip": "Place directional lights high above the scene for the most natural look."
            },
            {
                "title": "Organizing the Hierarchy",
                "content": """
<p>A clean hierarchy makes your scene easy to work with:</p>
<ul>
<li>Rename objects by clicking their name in the Properties panel.</li>
<li>Parent objects by creating them while a parent is selected, or by restructuring (coming soon).</li>
<li>Use descriptive names like "Ground", "Building_01", "Street_Lamp".</li>
<li>Group related objects under a common parent.</li>
</ul>
<p>Example hierarchy:<br>
<pre>
Root
 +-- Ground (Part)
 +-- Buildings
 |   +-- Building_01 (Part)
 |   +-- Roof_01 (Wedge)
 |   +-- Building_02 (Part)
 +-- Lighting
 |   +-- Sun (Light)
 +-- Decorations
     +-- Tree_01 (Part + Sphere)
</pre>
</p>
                """,
                "tip": "A well-organized hierarchy makes it easy to find and edit objects later."
            },
        ]
    },
    {
        "title": "Materials and Colors",
        "description": "Master materials, colors, transparency, and textures in Prima.",
        "overview": "Learn how to use Prima's material system to give your objects visually appealing surfaces. This covers colors, transparency, and how materials interact with lighting.",
        "steps": [
            {
                "title": "Understanding Materials",
                "content": """
<p>Every visible object in Prima has a <b>Material</b> that determines its appearance. Materials have these properties:</p>
<ul>
<li><b>Color</b> - The base color of the object (RGB).</li>
<li><b>Transparency</b> - How see-through the object is (0 = opaque, 1 = invisible).</li>
</ul>
<p>Materials interact with the scene's lighting. A red object will appear darker in shadowed areas and brighter where light hits it.</p>
<p>To change an object's material, select it and find the Material section in the Properties panel on the right.</p>
                """,
                "tip": "Lighter colors reflect more light; darker colors absorb more light."
            },
            {
                "title": "Changing Colors",
                "content": """
<p>Changing an object's color is easy:</p>
<ol>
<li>Select the object in the hierarchy.</li>
<li>In the Properties panel, find the <b>Material</b> section.</li>
<li>Click the <b>Change Color</b> button.</li>
<li>A color picker dialog appears. Choose a color and click OK.</li>
</ol>
<p>The object in the viewport updates immediately to show the new color.</p>
<p>Prima provides built-in material presets: Red, Green, Blue, White, Gray, Black, Yellow. You can access these programmatically in scripts.</p>
                """,
                "tip": "Use the color picker's eye-dropper tool to sample colors from anywhere on your screen."
            },
            {
                "title": "Using Transparency",
                "content": """
<p>Transparency creates glass-like or ghostly effects:</p>
<ol>
<li>Select an object.</li>
<li>In the Material section, find <b>Transparency</b>.</li>
<li>Set it to a value between 0 and 1:</li>
<ul>
<li><b>0.0</b> - Completely opaque (default)</li>
<li><b>0.5</b> - Semi-transparent (like tinted glass)</li>
<li><b>0.9</b> - Barely visible</li>
<li><b>1.0</b> - Completely invisible</li>
</ul>
</ol>
<p>Transparency is great for windows, force fields, water surfaces, and ghost effects.</p>
                """,
                "tip": "For a glass effect, use a light blue color with ~0.3-0.5 transparency."
            },
        ]
    },
    {
        "title": "Scripting with Python",
        "description": "Learn how to add interactivity to your Prima worlds using Python scripts.",
        "overview": "Prima uses Python for scripting, similar to how Roblox uses Lua. Attach scripts to objects to make them move, respond to events, and interact with each other.",
        "steps": [
            {
                "title": "Creating a Script",
                "content": """
<p>Scripts are Python code attached to objects:</p>
<ol>
<li>Right-click in the hierarchy and choose <b>Add Object > Script</b>.</li>
<li>A Script object appears. Select it to see the code editor.</li>
<li>The Properties panel now shows a text editor where you can type Python code.</li>
<li>Your script has access to the <code>engine</code>, <code>scene</code>, and <code>object</code> variables.</li>
</ol>
<p>Example script that prints a message:</p>
<pre>
print("Hello from Prima!")
print(f"I am attached to: {object.name}")
</pre>
                """,
                "tip": "Scripts run when the editor starts. Use the 'enabled' checkbox to turn them on/off."
            },
            {
                "title": "Working with Objects",
                "content": """
<p>In scripts, you can access and modify any object in the scene:</p>
<pre>
# Find objects by name
player = scene.find_by_name("Player Part")
if player:
    player.position = Vector3(0, 5, 0)

# Access the parent object
if object.parent:
    print(f"My parent is: {object.parent.name}")

# Iterate all objects
for obj in scene.get_all_objects():
    if obj.object_type == "Part":
        obj.visible = True
</pre>
<p>The <code>Vector3</code> class is always available for 3D math operations.</p>
                """,
                "tip": "Use <code>scene.find_by_name()</code> to quickly locate objects by their name."
            },
            {
                "title": "Making Objects Move",
                "content": """
<p>Create moving objects with simple position updates:</p>
<pre>
import math

obj = scene.find_by_name("My Part")
if obj:
    obj.velocity = Vector3(2, 0, 0)

time = 0
def update():
    global time
    obj = scene.find_by_name("My Part")
    if obj:
        time += 0.016
        obj.position = Vector3(
            math.sin(time) * 5,
            2 + math.sin(time * 2) * 1,
            0
        )
</pre>
<p>For smooth motion, update position every frame using time-based calculations.</p>
                """,
                "tip": "Use <code>math.sin()</code> for smooth back-and-forth motion."
            },
        ]
    },
]
