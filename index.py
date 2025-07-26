from PIL import Image
import numpy as np
import os
import glob
import pyperclip

def rgb_to_color_char(r, g, b, correct_from=None, correct_to=None):
    """Convert RGB values to the closest color character from the palette."""
    # Define the color palette (RGB values) - improved for better accuracy
    colors = {
        '0': (0, 0, 0),      # Black
        '1': (255, 255, 255), # White
        'r': (255, 0, 0),     # Red
        'o': (255, 165, 0),   # Orange
        'y': (255, 255, 0),   # Yellow
        'g': (0, 255, 0),     # Green
        'b': (0, 0, 255),     # Blue
        't': (0, 255, 255),   # Teal (cyan) - changed to be more distinct from green
        'p': (255, 0, 255)    # Purple (magenta) - changed to be more distinct
    }
    
    # Use HSV color space for better color matching
    def rgb_to_hsv(r, g, b):
        r, g, b = r/255.0, g/255.0, b/255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        if max_val == min_val:
            h = 0
        elif max_val == r:
            h = (60 * ((g-b)/diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b-r)/diff) + 120) % 360
        else:
            h = (60 * ((r-g)/diff) + 240) % 360
        
        s = 0 if max_val == 0 else diff / max_val
        v = max_val
        return h, s, v
    
    # Convert target color to HSV
    target_h, target_s, target_v = rgb_to_hsv(r, g, b)
    
    # If correction is set, check if this pixel should be corrected
    if correct_from and correct_to and correct_from in colors and correct_to in colors:
        correct_from_r, correct_from_g, correct_from_b = colors[correct_from]
        correct_from_h, correct_from_s, correct_from_v = rgb_to_hsv(correct_from_r, correct_from_g, correct_from_b)
        
        # Calculate distance to the color we want to correct from
        correct_distance = ((target_h - correct_from_h) ** 2 + 
                           (target_s - correct_from_s) ** 2 + 
                           (target_v - correct_from_v) ** 2) ** 0.5
        
        # If pixel is close to the color we want to correct from, convert it to the target color
        if correct_distance < 0.4:  # Threshold for color correction
            return correct_to
    
    # Define HSV ranges for each color - improved to better distinguish purple from blue
    color_ranges = {
        '0': {'h_range': None, 's_range': (0, 0.1), 'v_range': (0, 0.2)},  # Black
        '1': {'h_range': None, 's_range': (0, 0.1), 'v_range': (0.8, 1.0)}, # White
        'r': {'h_range': (330, 30), 's_range': (0.3, 1.0), 'v_range': (0.3, 1.0)},  # Red
        'o': {'h_range': (15, 45), 's_range': (0.3, 1.0), 'v_range': (0.3, 1.0)},   # Orange
        'y': {'h_range': (45, 75), 's_range': (0.3, 1.0), 'v_range': (0.3, 1.0)},   # Yellow
        'g': {'h_range': (75, 165), 's_range': (0.3, 1.0), 'v_range': (0.3, 1.0)},  # Green
        'b': {'h_range': (195, 255), 's_range': (0.3, 1.0), 'v_range': (0.3, 1.0)}, # Blue (narrowed range)
        't': {'h_range': (165, 195), 's_range': (0.3, 1.0), 'v_range': (0.3, 1.0)}, # Teal
        'p': {'h_range': (255, 330), 's_range': (0.3, 1.0), 'v_range': (0.3, 1.0)}  # Purple (adjusted range)
    }
    
    # Check if color matches any specific range
    for char, ranges in color_ranges.items():
        h_match = True
        s_match = ranges['s_range'][0] <= target_s <= ranges['s_range'][1]
        v_match = ranges['v_range'][0] <= target_v <= ranges['v_range'][1]
        
        if ranges['h_range'] is not None:
            h_min, h_max = ranges['h_range']
            if h_min <= h_max:
                h_match = h_min <= target_h <= h_max
            else:  # Handle wraparound (like red: 330-30)
                h_match = target_h >= h_min or target_h <= h_max
        
        if h_match and s_match and v_match:
            # If correction is set and this color is close to the color we want to correct from, use correction
            if correct_from and correct_to and correct_from != char:
                correct_from_r, correct_from_g, correct_from_b = colors[correct_from]
                correct_from_h, correct_from_s, correct_from_v = rgb_to_hsv(correct_from_r, correct_from_g, correct_from_b)
                current_r, current_g, current_b = colors[char]
                current_h, current_s, current_v = rgb_to_hsv(current_r, current_g, current_b)
                
                # Check if current color is close to the color we want to correct from
                color_distance = ((current_h - correct_from_h) ** 2 + 
                                (current_s - correct_from_s) ** 2 + 
                                (current_v - correct_from_v) ** 2) ** 0.5
                
                if color_distance < 0.4:  # If colors are similar, use correction
                    return correct_to
            return char
    
    # Fallback to distance-based matching for edge cases
    min_distance = float('inf')
    closest_color = '0'
    
    for char, (cr, cg, cb) in colors.items():
        distance = ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            closest_color = char
    
    # Final correction check - if correction color is somewhat close, use it
    if correct_from and correct_to and correct_from != closest_color:
        correct_from_r, correct_from_g, correct_from_b = colors[correct_from]
        correct_distance = ((r - correct_from_r) ** 2 + (g - correct_from_g) ** 2 + (b - correct_from_b) ** 2) ** 0.5
        if correct_distance < min_distance * 1.5:  # Allow correction if it's not too far off
            return correct_to
    
    return closest_color

def image_to_string(image_path, width=50, height=50, correct_from=None, correct_to=None):
    """Convert an image to a string representation using the specified color palette."""
    try:
        # Open and resize the image
        img = Image.open(image_path)
        img = img.resize((width, height))
        
        # Convert to RGB if it's not already, handling transparency
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to numpy array for easier processing
        img_array = np.array(img)
        
        # Convert each pixel to a color character
        result = ""
        for y in range(height):
            for x in range(width):
                r, g, b = img_array[y, x]
                result += rgb_to_color_char(r, g, b, correct_from, correct_to)
        
        return result
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def get_available_images():
    """Get list of image files in the current directory."""
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.tiff']
    images = []
    for ext in image_extensions:
        images.extend(glob.glob(ext))
    return sorted(images)

def complete_image_name(text, state):
    """Autocomplete function for image filenames."""
    images = get_available_images()
    matches = [img for img in images if img.startswith(text)]
    if state < len(matches):
        return matches[state]
    return None

def main():
    print("Available images in current directory:")
    images = get_available_images()
    if images:
        for i, img in enumerate(images, 1):
            print(f"{i}. {img}")
    else:
        print("No image files found in current directory")
        return
    
    print("\nEnter image filename or number:")
    user_input = input("> ").strip()
    
    if not user_input:
        print("No filename provided")
        return
    
    # Check if user entered a number
    try:
        num = int(user_input)
        if 1 <= num <= len(images):
            image_path = images[num - 1]
        else:
            print(f"Invalid number. Please enter a number between 1 and {len(images)}")
            return
    except ValueError:
        # User entered a filename
        image_path = user_input
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"File '{image_path}' not found")
        return
    
    # Choose color correction mode
    print("\nChoose color correction mode:")
    print("0. Normal mode (no correction)")
    print("1. Red")
    print("2. Orange") 
    print("3. Yellow")
    print("4. Green")
    print("5. Blue")
    print("6. Teal")
    print("7. Purple")
    
    print("\nStep 1: Which color in the image should be corrected?")
    correct_from_choice = input("Enter choice (0-7): ").strip()
    
    correct_from = None
    try:
        choice = int(correct_from_choice)
        color_map = {
            0: None,
            1: 'r',
            2: 'o', 
            3: 'y',
            4: 'g',
            5: 'b',
            6: 't',
            7: 'p'
        }
        if choice in color_map:
            correct_from = color_map[choice]
        else:
            print("Invalid choice, using normal mode")
    except ValueError:
        print("Invalid input, using normal mode")
    
    correct_to = None
    if correct_from:
        print(f"\nStep 2: What should {correct_from.upper()} be converted to?")
        correct_to_choice = input("Enter choice (1-7): ").strip()
        
        try:
            choice = int(correct_to_choice)
            if 1 <= choice <= 7:
                correct_to = color_map[choice]
            else:
                print("Invalid choice, using normal mode")
                correct_from = None
        except ValueError:
            print("Invalid input, using normal mode")
            correct_from = None
    
    # Convert image to string
    result = image_to_string(image_path, correct_from=correct_from, correct_to=correct_to)
    
    if result:
        if correct_from and correct_to:
            mode_text = f" ({correct_from.upper()} → {correct_to.upper()} correction)"
        else:
            mode_text = " (normal mode)"
        print(f"\nConverted image to string{mode_text}:")
        print(f'"{result}"')
        print(f"\nString length: {len(result)}")
        print(f"Expected length for 50x50: {50*50}")
        
        # Copy to clipboard
        try:
            pyperclip.copy("localStorage[\"submit-image\"] = " + ' \"' + result + '\"') # To add the quotes to the string and also localstorage for the console ofc
            print("✓ String copied to clipboard!")
        except Exception as e:
            print(f"Could not copy to clipboard: {e}")
            print("You can manually copy the string above.")
    else:
        print("Failed to convert image")

if __name__ == "__main__":
    main()
