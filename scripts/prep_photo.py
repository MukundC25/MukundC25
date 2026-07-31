"""
prep_photo.py — Prepare a portrait photo for ASCII conversion.

Steps:
1. Remove background with rembg (isolate subject).
2. Boost local contrast with CLAHE (gives flat faces real highlights/shadows).
3. Composite onto pure white so background maps to space characters.

Usage:
    python scripts/prep_photo.py <input_photo>
    # Outputs: source-prepped.png in the repo root
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep(input_path: str, output_path: str = "source-prepped.png") -> None:
    # --- 1. Remove background ---
    raw = Path(input_path).read_bytes()
    nobg = remove(raw)  # returns PNG bytes with alpha channel

    # Convert to PIL RGBA
    img = Image.open(__import__("io").BytesIO(nobg)).convert("RGBA")

    # --- 2. Composite onto white ---
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composite = Image.alpha_composite(white_bg, img).convert("L")  # grayscale

    # --- 3. Boost local contrast with CLAHE ---
    arr = np.array(composite)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(arr)

    # Save result
    out = Image.fromarray(enhanced)
    out.save(output_path)
    print(f"[prep_photo] Saved prepped image to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep(input_file, output_file)
