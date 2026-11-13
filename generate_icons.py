import os
from PIL import Image, ImageDraw, ImageFont

def make_icon(size, output_path):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer rounded rect background
    r = size // 5
    bg_color = (22, 72, 56, 255) # #164838 deep forest green
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=bg_color)
    
    # Inner accent badge
    margin = size // 4
    accent_color = (255, 255, 255, 255)
    
    # Draw a stylized briefcase / trail badge
    # Briefcase body
    bw = int(size * 0.54)
    bh = int(size * 0.38)
    bx = (size - bw) // 2
    by = int(size * 0.42)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=size // 18, fill=accent_color)
    
    # Briefcase handle
    hw = int(size * 0.26)
    hh = int(size * 0.16)
    hx = (size - hw) // 2
    hy = by - hh + int(size * 0.04)
    draw.rounded_rectangle([hx, hy, hx + hw, by + int(size * 0.04)], radius=size // 22, outline=accent_color, width=max(4, size // 32))
    
    # Center stripe / clasp
    cw = int(size * 0.10)
    ch = int(size * 0.14)
    cx = (size - cw) // 2
    cy = by + int(size * 0.08)
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=size // 40, fill=(31, 95, 74, 255))
    
    # Accent dot (status tracker badge)
    dot_r = int(size * 0.08)
    dx = bx + bw - dot_r - int(size * 0.02)
    dy = by - dot_r + int(size * 0.02)
    draw.ellipse([dx, dy, dx + dot_r * 2, dy + dot_r * 2], fill=(143, 199, 177, 255), outline=bg_color, width=max(2, size // 60))
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"Generated {output_path} ({size}x{size})")

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    www_icons = os.path.join(base, "www", "icons")
    make_icon(192, os.path.join(www_icons, "icon-192.png"))
    make_icon(512, os.path.join(www_icons, "icon-512.png"))
    make_icon(192, os.path.join(base, "icons", "icon-192.png"))
    make_icon(512, os.path.join(base, "icons", "icon-512.png"))
