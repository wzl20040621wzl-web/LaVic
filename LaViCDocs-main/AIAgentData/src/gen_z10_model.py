import trimesh
import numpy as np
import os

def create_z10_model(output_path):
    # Z-10 is a medium attack helicopter (narrow body, tandem cockpit)
    # Colors
    fuselage_color = [40, 40, 40, 255] # Dark Grey/Black
    rotor_color = [20, 20, 20, 255] # Black
    glass_color = [50, 50, 60, 150] # Dark transparent
    weapon_color = [30, 30, 30, 255] # Darker grey

    # 1. Fuselage (Narrow, streamlined)
    # Main body
    body = trimesh.creation.box(extents=[12.0, 1.5, 2.0])
    body.visual.face_colors = fuselage_color
    
    # Nose (Pointed/Sensor)
    nose = trimesh.creation.cone(radius=0.7, height=2.0)
    nose.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2, [0, 1, 0]))
    nose.apply_translation([7.0, 0, 0]) # Front
    nose.visual.face_colors = fuselage_color

    # Cockpit (Stepped - Tandem)
    # Rear cockpit (Pilot)
    cockpit_rear = trimesh.creation.box(extents=[2.0, 1.2, 1.2])
    cockpit_rear.apply_translation([2.0, 0, 1.5])
    cockpit_rear.visual.face_colors = glass_color
    
    # Front cockpit (Gunner) - lower than rear
    cockpit_front = trimesh.creation.box(extents=[2.0, 1.2, 1.0])
    cockpit_front.apply_translation([4.0, 0, 1.0])
    cockpit_front.visual.face_colors = glass_color

    # 2. Tail Boom
    tail_boom = trimesh.creation.cylinder(radius=0.5, height=8.0)
    tail_boom.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    tail_boom.apply_translation([-8.0, 0, 0.5]) 
    tail_boom.visual.face_colors = fuselage_color

    # Vertical Stabilizer
    v_stab = trimesh.creation.box(extents=[2.0, 0.2, 3.0])
    v_stab.apply_translation([-12.0, 0, 1.5])
    v_stab.visual.face_colors = fuselage_color
    
    # Horizontal Stabilizer
    h_stab = trimesh.creation.box(extents=[1.0, 3.0, 0.2])
    h_stab.apply_translation([-10.0, 0, 0.5])
    h_stab.visual.face_colors = fuselage_color

    # 3. Stub Wings
    wing_l = trimesh.creation.box(extents=[1.5, 4.0, 0.3])
    wing_l.apply_translation([1.0, 2.0, -0.2])
    wing_l.visual.face_colors = fuselage_color
    
    wing_r = trimesh.creation.box(extents=[1.5, 4.0, 0.3])
    wing_r.apply_translation([1.0, -2.0, -0.2])
    wing_r.visual.face_colors = fuselage_color
    
    # Weapons (Rocket pods/Missiles)
    pod_l = trimesh.creation.cylinder(radius=0.3, height=1.5)
    pod_l.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    pod_l.apply_translation([1.0, 3.0, -0.8])
    pod_l.visual.face_colors = weapon_color
    
    pod_r = trimesh.creation.cylinder(radius=0.3, height=1.5)
    pod_r.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    pod_r.apply_translation([1.0, -3.0, -0.8])
    pod_r.visual.face_colors = weapon_color

    # 4. Main Rotor (5 blades)
    # Rotor mast
    mast = trimesh.creation.cylinder(radius=0.3, height=1.5)
    mast.apply_translation([1.0, 0, 1.8])
    mast.visual.face_colors = fuselage_color

    # Blades
    blades = []
    for i in range(5):
        angle = i * (2 * np.pi / 5)
        blade = trimesh.creation.box(extents=[8.0, 0.5, 0.1])
        blade.apply_translation([4.0, 0, 0])
        blade.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
        blade.apply_translation([1.0, 0, 2.5]) # On top of mast
        blade.visual.face_colors = rotor_color
        blades.append(blade)

    # 5. Tail Rotor (4 blades, X config approximated)
    tail_rotor_center = [-12.0, 0.3, 2.5]
    tail_blades = []
    for i in range(4): 
        angle = i * (2 * np.pi / 4)
        t_blade = trimesh.creation.box(extents=[1.2, 0.2, 0.05])
        t_blade.apply_translation([0.6, 0, 0])
        t_blade.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 1, 0])) # Rotate in Y plane
        t_blade.apply_translation(tail_rotor_center)
        t_blade.visual.face_colors = rotor_color
        tail_blades.append(t_blade)

    # Combine all
    parts = [body, nose, cockpit_rear, cockpit_front, tail_boom, v_stab, h_stab, wing_l, wing_r, pod_l, pod_r, mast] + blades + tail_blades
    mesh = trimesh.util.concatenate(parts)
    
    # Export
    mesh.export(output_path)
    print(f"Generated Z-10 model at {output_path}")

if __name__ == "__main__":
    output_dir = r"F:\LaVic\LaViCDocs-main\AIAgentData\models\Z-10_Helicopter\Z-10_Helicopter"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    glb_path = os.path.join(output_dir, "Z-10_Helicopter.glb")
    create_z10_model(glb_path)
