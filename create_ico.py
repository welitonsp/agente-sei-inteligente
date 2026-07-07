import sys
from PIL import Image

def create_icon(input_path, output_path):
    try:
        img = Image.open(input_path)
        img.save(output_path, format='ICO', sizes=[(256, 256)])
        print("Icon created successfully.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_ico.py <input.jpg> <output.ico>")
        sys.exit(1)
    create_icon(sys.argv[1], sys.argv[2])
