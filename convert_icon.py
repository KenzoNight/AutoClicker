from PIL import Image
import os

# Source path (uploaded metadata)
src = r"C:/Users/pc/.gemini/antigravity/brain/a998267b-cda4-4eb5-9324-170a4f7948e4/uploaded_media_1770204431115.png"
# Destination path for folder icon
dst = r"c:\Users\pc\.gemini\antigravity\scratch\autoclicker\folder.ico"

try:
    img = Image.open(src)
    img.save(dst, format='ICO')
    print(f"Successfully converted {src} to {dst}")
except Exception as e:
    print(f"Error converting icon: {e}")
