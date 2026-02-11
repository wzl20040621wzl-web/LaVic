import trimesh
import numpy as np
import os

def create_z8l_model(output_path):
    # Z-8L is a large transport helicopter
    # Colors
    fuselage_color = [50, 60, 50, 255] # Dark green
    rotor_color = [20, 20, 20, 255] # Black
    glass_color = [100, 100, 200, 150] # Semi-transparent blue

    # 1. Fuselage (Box-like with rounded bottom, approximated by a scaled cylinder/box combination)
    # Main body
    body = trimesh.creation.box(extents=[18.0, 4.0, 4.5])
    body.visual.face_colors = fuselage_color
    
    # Nose (Rounded)
    nose = trimesh.creation.icosphere(radius=2.2, subdivisions=2)
    nose.apply_scale([1.5, 1.0, 1.0])
    nose.apply_translation([9.0, 0, 0]) # Front
    nose.visual.face_colors = fuselage_color

    # Cockpit windows (Box)
    cockpit = trimesh.creation.box(extents=[2.0, 3.0, 1.5])
    cockpit.apply_translation([8.0, 0, 2.0])
    cockpit.visual.face_colors = glass_color

    # 2. Tail Boom
    tail_boom = trimesh.creation.cylinder(radius=1.0, height=12.0)
    tail_boom.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    tail_boom.apply_translation([-12.0, 0, 1.5]) # Extend to rear and slightly up
    tail_boom.visual.face_colors = fuselage_color

    # Vertical Stabilizer
    v_stab = trimesh.creation.box(extents=[3.0, 0.5, 5.0])
    v_stab.apply_translation([-18.0, 0, 4.0])
    v_stab.visual.face_colors = fuselage_color

    # 3. Main Rotor
    # Rotor mast
    mast = trimesh.creation.cylinder(radius=0.5, height=2.0)
    mast.apply_translation([0, 0, 2.5])
    mast.visual.face_colors = fuselage_color

    # Blades (6 blades)
    blades = []
    for i in range(6):
        angle = i * (2 * np.pi / 6)
        blade = trimesh.creation.box(extents=[10.0, 0.8, 0.1])
        # Move blade out so it starts from center
        blade.apply_translation([5.0, 0, 0])
        # Rotate around Z axis
        blade.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
        blade.apply_translation([0, 0, 3.5]) # On top of mast
        blade.visual.face_colors = rotor_color
        blades.append(blade)

    # 4. Tail Rotor (on vertical stabilizer)
    tail_rotor_center = [-18.0, 0.5, 5.5]
    tail_blades = []
    for i in range(5): # 5 blades
        angle = i * (2 * np.pi / 5)
        t_blade = trimesh.creation.box(extents=[2.0, 0.3, 0.05])
        t_blade.apply_translation([1.0, 0, 0])
        t_blade.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 1, 0])) # Rotate in Y plane (side facing)
        t_blade.apply_translation(tail_rotor_center)
        t_blade.visual.face_colors = rotor_color
        tail_blades.append(t_blade)

    # 5. Sponsons (Fuel tanks/Gear)
    sponson_l = trimesh.creation.cylinder(radius=1.2, height=8.0)
    sponson_l.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    sponson_l.apply_translation([0, 2.5, -1.5])
    sponson_l.visual.face_colors = fuselage_color

    sponson_r = trimesh.creation.cylinder(radius=1.2, height=8.0)
    sponson_r.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    sponson_r.apply_translation([0, -2.5, -1.5])
    sponson_r.visual.face_colors = fuselage_color

    # Combine all
    parts = [body, nose, cockpit, tail_boom, v_stab, mast, sponson_l, sponson_r] + blades + tail_blades
    mesh = trimesh.util.concatenate(parts)
    
    # Export
    mesh.export(output_path)
    print(f"Generated Z-8L model at {output_path}")

if __name__ == "__main__":
    output_dir = r"F:\LaVic\LaViCDocs-main\AIAgentData\models\Z-8L_Helicopter\Z-8L_Helicopter"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    glb_path = os.path.join(output_dir, "Z-8L_Helicopter.glb")
    create_z8l_model(glb_path)
