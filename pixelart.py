import requests
from io import BytesIO
from collections import Counter
from PIL import Image
from PIL import ImageDraw, ImageFont
import math
import random

# Eine Liste der verfügbaren Blöcke und Farben in BattleminerZ
BLOCKS = {
    'BLACK': (0, 0, 0), 'BRICK': (180, 41, 10), 'BROWN': (163, 105, 55), 'CHISLEDBRICK': (224, 224, 224), 'CHISLEDVOLCANICBRICK': (75, 17, 2), 'CHSILEDSANSTONE': (223, 191, 111), 'COPPERORE': (155, 161, 139), 'CYAN': (104, 194, 203), 'DARKBLUE': (16, 41, 255), 'DARKBROWN': (109, 84, 10), 'DARKCHISLEDBRICK': (166, 166, 166), 'DARKGREEN': (91, 173, 91), 'DARKGREY': (139, 139, 139), 'DARKPURPLE': (137, 128, 203), 'DARKRED': (203, 128, 120), 'DARKYELLOW': (205, 213, 139), 'DIAMONDBLOCK': (136, 249, 249), 'DIAMONDORE': (142, 172, 168), 'EXPLOSIVE': (119, 59, 22), 'GLASS': (240, 240, 240), 'GOLDBLOCK': (249, 246, 88), 'GOLDORE': (165, 162, 138), 'GRASSSIDE': (191, 127, 55), 'GRAVEL': (158, 154, 153), 'IRONBLOCK': (211, 211, 211), 'IRONORE': (156, 141, 131), 'LEAVES': (72, 154, 14), 'LIGHTGREEN': (2, 255, 2), 'ORANGE': (255, 121, 2), 'PINK': (255, 153, 227), 'PLANK': (144, 63, 42), 'PURPLE': (141, 0, 209), 'RED': (253, 0, 0), 'ROCKS': (162, 148, 155), 'SAND': (233, 200, 115), 'SMOOTHSTONE': (167, 167, 167), 'SNOW': (237, 237, 237), 'WHITE': (255, 255, 255), 'WOODSIDE': (161, 64, 62), 'WOODTOP': (243, 167, 4), 'ZINCORE': (168, 165, 164)
}

def get_closest_block(pixel_color):
    min_distance = float("inf")
    closest_block = None
    for block, block_color in BLOCKS.items():
        distance = sum([(pixel_color[i] - block_color[i])**2 for i in range(3)])
        if distance < min_distance:
            min_distance = distance
            closest_block = block
    return closest_block

def convert_image_to_map(image_path):
    img = Image.open(image_path)
    img = img.convert("RGBA")
    width, height = img.size
    map_data = []

    for y in range(height):
        row = []
        for x in range(width):
            pixel_color = img.getpixel((x, y))
            if pixel_color[3] == 0:
                closest_block = 'TRANSPARENT'
            else:
                closest_block = get_closest_block(pixel_color)
            row.append(closest_block)
        map_data.append(row)

    return map_data

def load_textures():
    textures = {}
    for block in BLOCKS:
        try:
            texture = Image.open(f"textures/{block}.png")
            texture = texture.convert("RGBA")
            textures[block] = texture
        except FileNotFoundError:
            print(f"Warnung: Textur für {block} nicht gefunden.")
    return textures

def create_visual_map(block_map, textures):
    block_size = textures[list(textures.keys())[0]].size
    width, height = len(block_map[0]) * block_size[0], len(block_map) * block_size[1]
    visual_map = Image.new("RGBA", (width, height))

    for y, row in enumerate(block_map):
        for x, block in enumerate(row):
            if block != 'TRANSPARENT':
                texture = textures[block]
                visual_map.paste(texture, (x * block_size[0], y * block_size[1]), texture)

    return visual_map

def get_block_counts(block_map):
    block_counts = Counter()
    for row in block_map:
        block_counts.update(row)
    del block_counts['TRANSPARENT']
    return block_counts

def draw_line(draw, start, end, line_color, line_width=2):
    draw.line([start, end], fill=line_color, width=line_width)

def get_random_color():
    return tuple(random.randint(0, 255) for _ in range(3))

def create_visual_map_with_extra_space(block_map, textures):
    block_size = textures[list(textures.keys())[0]].size
    width, height = len(block_map[0]) * block_size[0], len(block_map) * block_size[1]
    extra_space = 220  # Breite des zusätzlichen Bereichs für die Liste
    visual_map = Image.new("RGBA", (width + extra_space, height))

    for y, row in enumerate(block_map):
        for x, block in enumerate(row):
            if block != 'TRANSPARENT':
                texture = textures[block]
                visual_map.paste(texture, (x * block_size[0], y * block_size[1]), texture)

    return visual_map
    
def add_texture_labels(visual_map, block_map, textures):
    draw = ImageDraw.Draw(visual_map)
    font = ImageFont.truetype("arial.ttf", size=18)
    block_size = textures[list(textures.keys())[0]].size
    block_counts = get_block_counts(block_map)

    results_offset_x = visual_map.width - 240  # Verschieben Sie den Hintergrund weiter nach links
    results_offset_y = 10

    # Ändern Sie die Hintergrundfarbe in eine angenehme Dark-Mode-Farbe
    dark_mode_color = (18, 18, 18, 255)  # RGB-Farbwert für angenehmen Dark-Mode

    # Hintergrund für den Textbereich hinzufügen
    text_bg = Image.new("RGBA", (235, len(block_counts) * 20 + 10), dark_mode_color)
    visual_map.paste(text_bg, (results_offset_x - 5, results_offset_y), text_bg)

    for index, (block, count) in enumerate(block_counts.items()):
        first_block = True
        line_color = BLOCKS[block]
        for y, row in enumerate(block_map):
            for x, block_in_map in enumerate(row):
                if block_in_map == block and first_block:
                    texture = textures[block]
                    start = (x * block_size[0] + block_size[0] // 2, y * block_size[1] + block_size[1] // 2)
                    end = (results_offset_x - texture.width - 10, results_offset_y + 20 * index + texture.height // 2)
                    draw_line(draw, start, end, line_color, line_width=2)
                    
                    # Textur neben der Auflistung anzeigen
                    texture_offset = (results_offset_x - texture.width - 5, results_offset_y + 20 * index)
                    visual_map.paste(texture, texture_offset, texture)
                    
                    text_position = (results_offset_x + 5, results_offset_y + 20 * index)
                    draw.text(text_position, f"{block} ({count}x)", font=font, fill=line_color)
                    first_block = False
                    break
            if not first_block:
                break

def main():
    image_path = "C:\\Users\\letsf\\Desktop\\App Shit\\pixelart\\pixelart\\pixil-frame-0 (1).png"
    block_map = convert_image_to_map(image_path)

    textures = load_textures()
    visual_map = create_visual_map_with_extra_space(block_map, textures)  # Use the new function

    add_texture_labels(visual_map, block_map, textures)  # Add texture labels with lines

    visual_map.save("visual_map.png")
    visual_map.show()

    block_counts = get_block_counts(block_map)
    for block, count in block_counts.items():
        print(f"{count}x {block}")

if __name__ == "__main__":
    main()