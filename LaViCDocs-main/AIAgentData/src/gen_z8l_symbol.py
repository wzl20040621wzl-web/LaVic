from PIL import Image, ImageDraw, ImageFont
import os

def create_z8l_symbol(output_path, is_thumbnail=False):
    width = 256
    height = 256
    
    if is_thumbnail:
        width = 800
        height = 600
        bg_color = (200, 200, 200, 255) # Light gray for thumbnail
    else:
        bg_color = (0, 0, 0, 0) # Transparent for symbol (but let's use white/transparent)

    img = Image.new('RGBA', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    if is_thumbnail:
        # Draw a simplified side view of helicopter
        # Body
        draw.ellipse([200, 250, 600, 450], fill=(50, 60, 50), outline=(0,0,0))
        # Tail
        draw.polygon([(250, 300), (100, 250), (100, 300)], fill=(50, 60, 50), outline=(0,0,0))
        # Rotor mast
        draw.rectangle([390, 200, 410, 250], fill=(20, 20, 20))
        # Rotor blades
        draw.rectangle([150, 200, 650, 210], fill=(20, 20, 20))
        # Text
        draw.text((350, 500), "Z-8L", fill=(0, 0, 0))
    else:
        # Draw Military Symbol (APP-6D Friendly Rotary Wing)
        # Blue Frame (Rectangle)
        frame_color = (0, 128, 255) # Blue
        draw.rectangle([20, 60, 236, 196], outline=frame_color, width=5)
        
        # Icon (Bowtie / Hourglass for Rotary Wing)
        # Center: 128, 128
        # Size: approx 100x100
        # Draw two triangles meeting at center
        icon_color = frame_color
        
        # Left triangle (point to right)
        draw.polygon([(78, 78), (78, 178), (128, 128)], fill=icon_color)
        # Right triangle (point to left)
        draw.polygon([(178, 78), (178, 178), (128, 128)], fill=icon_color)
        
        # Horizontal line (optional, for some variants, but simple bowtie is standard for rotary wing aviation)
        
    img.save(output_path)
    print(f"Generated image at {output_path}")

if __name__ == "__main__":
    output_dir = r"F:\LaVic\LaViCDocs-main\AIAgentData\models\Z-8L_Helicopter\Z-8L_Helicopter"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Generate Symbol
    sym_path = os.path.join(output_dir, "Z-8L_Helicopter_mil.png")
    create_z8l_symbol(sym_path, is_thumbnail=False)
    
    # Generate Thumbnail
    thumb_path = os.path.join(output_dir, "Z-8L_Helicopter.png")
    create_z8l_symbol(thumb_path, is_thumbnail=True)
