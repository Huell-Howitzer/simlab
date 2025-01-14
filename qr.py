import sys
from PIL import Image
from pyzbar.pyzbar import decode
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

def read_qr_code(image_path):
    """Reads and prints the contents of a QR code from an image file."""
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    decoded_objects = decode(img)

    if decoded_objects:
        for obj in decoded_objects:
            print(f"Type: {obj.type}")
            try:
                data = obj.data.decode('utf-8')
            except UnicodeDecodeError:
                data = obj.data
            print(f"Data: {data}")
    else:
        print("No QR code found or it may be too damaged to read.")

def string_to_qr_jpg(data, filename="qrcode.jpg", 
                     error_correction=ERROR_CORRECT_M, 
                     box_size=10, border=4):
    """
    Generates a QR code from the given data string and saves it as a JPG file.
    """
    qr = qrcode.QRCode(
        version=None,  # Automatic size determination
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img.save(filename, format="JPEG")
    print(f"QR code saved as {filename}")

def print_usage():
    print("Usage:")
    print("  To read a QR code from an image:")
    print("    python qr_tool.py read <image_file>")
    print()
    print("  To generate a QR code from a string:")
    print("    python qr_tool.py write <data_string> [output_filename]")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "read":
        image_file = sys.argv[2]
        read_qr_code(image_file)

    elif mode == "write":
        data = sys.argv[2]
        # Use provided filename if given, otherwise default to 'qrcode.jpg'
        filename = sys.argv[3] if len(sys.argv) > 3 else "qrcode.jpg"
        string_to_qr_jpg(data, filename)
    else:
        print("Invalid mode selected.")
        print_usage()