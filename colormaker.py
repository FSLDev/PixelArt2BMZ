from PIL import Image
import os

def get_average_color(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")
    width, height = img.size
    total_pixels = width * height
    r_total, g_total, b_total = 0, 0, 0

    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            r_total += r
            g_total += g
            b_total += b

    r_avg = r_total // total_pixels
    g_avg = g_total // total_pixels
    b_avg = b_total // total_pixels

    return r_avg, g_avg, b_avg

def main():
    texture_folder = "C:\\Users\\letsf\\Desktop\\App Shit\\pixelart\\textures"
    texture_files = [f for f in os.listdir(texture_folder) if f.endswith(".png")]

    block_colors = {}
    for texture_file in texture_files:
        block_name = os.path.splitext(texture_file)[0].upper()
        texture_path = os.path.join(texture_folder, texture_file)
        block_colors[block_name] = get_average_color(texture_path)

    print(block_colors)

if __name__ == "__main__":
    main()
