#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_image(text, filename, color="lightblue"):
    """
    Create a sample image with text overlay for testing purposes.
    
    Args:
        text (str): Text to display on the image
        filename (str): Path where to save the image file
        color (str): Background color for the image (default: lightblue)
    
    Returns:
        None: Saves the image to the specified filename
    """
    img = Image.new('RGB', (600, 400), color=color)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Text zentriert zeichnen
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (600 - text_width) // 2
    y = (400 - text_height) // 2
    
    draw.text((x, y), text, fill="black", font=font)
    img.save(filename)

# Ordner erstellen
base_path = "data/images"
os.makedirs(f"{base_path}/quellen", exist_ok=True)
os.makedirs(f"{base_path}/fundstellen", exist_ok=True)

# Beispielbilder basierend auf cases.json erstellen
cases = [
    ("Handelsregister_Wien_FP1", "HRB_123456_Seite_45"),
    ("Grundbuch_Graz_Ost_NEU", "GB_789_2023_Einlage_12"),
    ("Firmenbuch_Linz", "FN_456789x_Auszug_vom_15_07_2025"),
]

for quelle, fundstelle in cases:
    create_sample_image(f"QUELLE\n{quelle.replace('_', ' ')}", 
                       f"{base_path}/quellen/{quelle}.png", "lightgreen")
    create_sample_image(f"FUNDSTELLE\n{fundstelle.replace('_', ' ')}", 
                       f"{base_path}/fundstellen/{fundstelle}.png", "lightcoral")

print("✅ Beispielbilder erstellt")
