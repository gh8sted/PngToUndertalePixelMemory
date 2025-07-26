# PngToUndertalePixelMemory

Convert PNG images to pixel art for [Memories.undertale.com](https://memories.undertale.com/)

## How to Use

1. **Install Python packages:**
   ```
   pip install Pillow numpy pyperclip
   ```

2. **Put your PNG image** in the same folder as `index.py`

3. **Run the program:**
   ```
   python index.py
   ```

4. **Select your image:**
   - Type the filename (like `myimage.png`)
   - Or type the number from the list

5. **Choose color correction (optional):**
   - Step 1: Pick which color in your image to change
   - Step 2: Pick what color to change it to
   - Type `0` to skip color correction

6. **Use on the website:**
   - The result is copied to your clipboard automatically
   - Go to [https://memories.undertale.com/](https://memories.undertale.com/)
   - Press F12 to open console
   - Paste and press Enter
   - Refresh the page to see your pixel art

## Color Correction

If your image has the wrong colors, you can fix them:

- **Example:** If green pixels look like teal, choose green → teal correction
- **Example:** If purple pixels look like blue, choose purple → purple to keep them purple

## Available Colors

- `0` = Black
- `1` = White  
- `r` = Red
- `o` = Orange
- `y` = Yellow
- `g` = Green
- `b` = Blue
- `t` = Teal
- `p` = Purple

## Important

- Don't draw on the canvas after pasting - it will erase your image
- Images are automatically resized to 50x50 pixels
- Works with PNG, JPG, JPEG, BMP, GIF, TIFF files 
