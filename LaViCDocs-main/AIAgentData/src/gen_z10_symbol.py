from PIL import Image, ImageDraw, ImageFont
import os

def create_z10_symbol(output_path, is_thumbnail=False):
    width = 256
    height = 256
    
    if is_thumbnail:
        width = 800
        height = 600
        bg_color = (200, 200, 200, 255) # Light gray
    else:
        bg_color = (0, 0, 0, 0) # Transparent

    img = Image.new('RGBA', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    if is_thumbnail:
        # Draw a simplified side view of Z-10 (Attack Heli)
        # Body (Slender)
        draw.ellipse([250, 280, 550, 380], fill=(40, 40, 40), outline=(0,0,0))
        # Tail boom (Longer, thinner)
        draw.polygon([(250, 330), (100, 300), (100, 360)], fill=(40, 40, 40), outline=(0,0,0))
        # Vertical Stabilizer
        draw.polygon([(100, 300), (80, 200), (120, 300)], fill=(40, 40, 40), outline=(0,0,0))
        
        # Cockpit (Stepped)
        draw.polygon([(400, 280), (450, 250), (480, 250), (480, 280)], fill=(50, 50, 60), outline=(0,0,0))
        draw.polygon([(480, 280), (480, 260), (520, 260), (520, 300)], fill=(50, 50, 60), outline=(0,0,0))
        
        # Rotor mast
        draw.rectangle([390, 250, 410, 280], fill=(20, 20, 20))
        # Rotor blades
        draw.rectangle([150, 250, 650, 260], fill=(20, 20, 20))
        
        # Stub wings / Weapons
        draw.rectangle([350, 350, 450, 370], fill=(30, 30, 30))
        
        # Text
        # draw.text((350, 500), "Z-10", fill=(0, 0, 0)) # Need font, skip for now to avoid error
    else:
        # Draw Military Symbol (APP-6D Friendly Attack Helicopter)
        # Blue Frame (Rectangle)
        frame_color = (0, 128, 255) # Blue
        draw.rectangle([20, 60, 236, 196], outline=frame_color, width=5)
        
        # Icon (Rotary Wing - Bowtie)
        icon_color = frame_color
        
        # Left triangle
        draw.polygon([(78, 78), (78, 178), (128, 128)], fill=icon_color)
        # Right triangle
        draw.polygon([(178, 78), (178, 178), (128, 128)], fill=icon_color)
        
        # Attack Modifier "A"
        # Draw lines for A
        draw.line([(128, 70), (108, 110)], fill=icon_color, width=3)
        draw.line([(128, 70), (148, 110)], fill=icon_color, width=3)
        draw.line([(118, 90), (138, 90)], fill=icon_color, width=3)
        
    img.save(output_path)
    print(f"Generated image at {output_path}")

if __name__ == "__main__":
    output_dir = r"F:\LaVic\LaViCDocs-main\AIAgentData\models\Z-10_Helicopter\Z-10_Helicopter"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Generate Symbol
    sym_path = os.path.join(output_dir, "Z-10_Helicopter_mil.png")
    create_z10_symbol(sym_path, is_thumbnail=False)
    
    # Generate Thumbnail
    thumb_path = os.path.join(output_dir, "Z-10_Helicopter.png")
    create_z10_symbol(thumb_path, is_thumbnail=True)
