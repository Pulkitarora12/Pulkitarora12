"""Prep a portrait photo for ASCII conversion:
1. Remove background (rembg)
2. CLAHE local-contrast boost
3. Composite onto white so background maps to blank ASCII glyph
Output: source-prepped.png (grayscale)
"""
import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove

def main(src_path, out_path="source-prepped.png"):
    im = Image.open(src_path).convert("RGB")
    no_bg = remove(im)  # RGBA, subject isolated

    # Composite onto pure white using alpha channel
    rgba = np.array(no_bg)
    alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
    rgb = rgba[:, :, :3].astype(np.float32)
    white = np.ones_like(rgb) * 255.0
    composited = (rgb * alpha + white * (1 - alpha)).astype(np.uint8)

    gray = cv2.cvtColor(composited, cv2.COLOR_RGB2GRAY)

    # CLAHE for local contrast so a flatly-lit face gets real highlights/shadows
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray_clahe = clahe.apply(gray)

    # Re-flatten background to pure white (CLAHE can slightly darken it)
    alpha_mask = (alpha.squeeze() > 0.15)
    gray_clahe = np.where(alpha_mask, gray_clahe, 255).astype(np.uint8)

    Image.fromarray(gray_clahe).save(out_path)
    print(f"wrote {out_path} {gray_clahe.shape}")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.png"
    main(src)
