"""Aggressively crop white space from ardrazine images."""

from PIL import Image
import os

ARDRAZINE_DIR = r"e:\WEBSITE OSIS SMA IGS\web-ardraxis-prod\static\img\ardrazine"

def crop_whitespace_aggressive(image):
    """Crop white space from image edges with more aggressive threshold."""
    # Convert to RGBA if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Get data as array
    data = list(image.getdata())
    
    # Find bounds of non-white pixels (more aggressive threshold: 240 instead of 250)
    width, height = image.size
    left = width
    top = height
    right = 0
    bottom = 0
    
    for y in range(height):
        for x in range(width):
            pixel = data[y * width + x]
            # Check if pixel is not white (with more aggressive tolerance)
            if pixel[3] > 0 and (pixel[0] < 240 or pixel[1] < 240 or pixel[2] < 240):
                if x < left:
                    left = x
                if x > right:
                    right = x
                if y < top:
                    top = y
                if y > bottom:
                    bottom = y
    
    # If no non-white pixels found, return original
    if left >= right or top >= bottom:
        return image
    
    # Add small padding (2px) to avoid cutting too close
    padding = 2
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(width, right + padding + 1)
    bottom = min(height, bottom + padding + 1)
    
    # Crop the image
    cropped = image.crop((left, top, right, bottom))
    return cropped

def main():
    files = sorted([f for f in os.listdir(ARDRAZINE_DIR) if f.endswith('.webp')])
    
    for filename in files:
        filepath = os.path.join(ARDRAZINE_DIR, filename)
        
        try:
            img = Image.open(filepath)
            original_size = img.size
            
            cropped = crop_whitespace_aggressive(img)
            new_size = cropped.size
            
            # Save cropped image
            cropped.save(filepath, 'WEBP', quality=95)
            
            print(f"{filename}: {original_size} -> {new_size}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
