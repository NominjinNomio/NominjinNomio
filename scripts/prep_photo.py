"""
Removes the background from source-photo.jpg, producing source-prepped.png.
Usage: python prep_photo.py <input_photo> <output_png>
"""
import sys
from rembg import remove
from PIL import Image


def main():
    if len(sys.argv) != 3:
        print("Usage: python prep_photo.py <input_photo> <output_png>")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]
    img = Image.open(input_path)
    out = remove(img)
    out.save(output_path)
    print(f"Wrote {output_path} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
