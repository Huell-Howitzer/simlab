#!/usr/bin/env python3
"""
A minimal QR Code generator written entirely in Python.
This implementation:
  • only supports Version 1 (21×21 modules)
  • only supports byte mode encoding (max 17 bytes)
  • uses error‐correction level L (7 ECC codewords)
  • uses a fixed mask (mask 0)

Because the QR Code specification is quite involved, this code is simplified and
is intended for educational purposes rather than production use.
"""

import sys
from PIL import Image, ImageDraw

# -----------------------------
# Global constants for Version 1
# -----------------------------
VERSION = 1
SIZE = 21       # QR Code version 1 is 21×21 modules.
DATA_CODEWORDS = 19  # For version 1-L, 19 data codewords (of 8 bits each)
ECC_CODEWORDS = 7    # For version 1-L, 7 error-correction codewords

# -------------------------------------
# GF(256) arithmetic (using primitive poly 0x11d)
# -------------------------------------
# We precompute exponent and logarithm tables for fast GF(256) arithmetic.
EXP_TABLE = [0] * 512
LOG_TABLE = [0] * 256

def init_gf256():
    x = 1
    for i in range(255):
        EXP_TABLE[i] = x
        LOG_TABLE[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11d
    for i in range(255, 512):
        EXP_TABLE[i] = EXP_TABLE[i - 255]

init_gf256()

def gf_mul(a, b):
    """Multiply two numbers in GF(256)."""
    if a == 0 or b == 0:
        return 0
    return EXP_TABLE[(LOG_TABLE[a] + LOG_TABLE[b]) % 255]

def gf_poly_mul(p, q):
    """Multiply two polynomials, p and q, in GF(256). 
       The polynomials are represented as lists of coefficients (from highest degree to constant)."""
    result = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        for j in range(len(q)):
            result[i + j] ^= gf_mul(p[i], q[j])
    return result

def rs_generator_poly(nsym):
    """Generate an RS (Reed–Solomon) generator polynomial for nsym error-correction codewords."""
    g = [1]
    for i in range(nsym):
        g = gf_poly_mul(g, [1, EXP_TABLE[i]])
    return g

# -------------------------------------
# Data encoding (Version 1, Byte mode)
# -------------------------------------
def encode_data(data):
    """
    Encode a text string into a list of 8‐bit codewords.
    For Version 1 byte mode:
      – Mode indicator: 4 bits ("0100")
      – Character count: 8 bits (since version 1)
      – Data: 8 bits per character (only ASCII supported)
    Then terminator and padding are added until there are 19 codewords.
    """
    if len(data) > 17:
        raise ValueError("Data too long for Version 1 (max 17 characters in byte mode).")
    bits = ""
    bits += "0100"  # mode indicator for byte mode
    bits += format(len(data), "08b")  # 8-bit character count

    for ch in data:
        bits += format(ord(ch), "08b")
    
    # Add terminator (up to 4 zero bits)
    terminator_len = min(4, DATA_CODEWORDS * 8 - len(bits))
    bits += "0" * terminator_len

    # Pad so that the bit-length is a multiple of 8.
    while len(bits) % 8 != 0:
        bits += "0"

    # Convert bits to codewords (bytes)
    codewords = []
    for i in range(0, len(bits), 8):
        codewords.append(int(bits[i:i+8], 2))

    # Pad with alternating bytes 0xEC and 0x11 until we have 19 codewords.
    pad_bytes = [0xEC, 0x11]
    pad_index = 0
    while len(codewords) < DATA_CODEWORDS:
        codewords.append(pad_bytes[pad_index % 2])
        pad_index += 1

    return codewords

# -------------------------------------
# Error correction codewords via Reed–Solomon
# -------------------------------------
def calculate_ecc(data_codewords, nsym):
    """
    Given the data codewords, compute the nsym error-correction codewords.
    (This uses the standard polynomial division algorithm for RS codes.)
    """
    gen = rs_generator_poly(nsym)
    # Make a copy of the data with space for ECC.
    msg = data_codewords + [0] * nsym
    for i in range(len(data_codewords)):
        coef = msg[i]
        if coef != 0:
            for j in range(len(gen)):
                msg[i+j] ^= gf_mul(gen[j], coef)
    ecc = msg[-nsym:]
    return ecc

def create_final_message(data):
    """
    Return the complete message (data codewords + ECC codewords)
    as a list of codewords.
    """
    data_codewords = encode_data(data)
    ecc_codewords = calculate_ecc(data_codewords, ECC_CODEWORDS)
    return data_codewords + ecc_codewords

def get_data_bit_list(final_message):
    """
    Convert the list of final codewords into a list of bits.
    """
    bits = ""
    for cw in final_message:
        bits += format(cw, "08b")
    return [int(b) for b in bits]

# -------------------------------------
# Build QR Code matrix (Version 1 – 21×21)
# -------------------------------------
def create_empty_matrix():
    """
    Create a SIZE×SIZE matrix initialized to None.
    Also create a matching “reserved” matrix to mark function (non‐data) modules.
    """
    matrix = [[None for _ in range(SIZE)] for _ in range(SIZE)]
    reserved = [[False for _ in range(SIZE)] for _ in range(SIZE)]
    return matrix, reserved

def add_finder_pattern(matrix, reserved, x, y):
    """Draw a 7×7 finder pattern at top‐left coordinate (x,y)."""
    pattern = [
        [1,1,1,1,1,1,1],
        [1,0,0,0,0,0,1],
        [1,0,1,1,1,0,1],
        [1,0,1,1,1,0,1],
        [1,0,1,1,1,0,1],
        [1,0,0,0,0,0,1],
        [1,1,1,1,1,1,1],
    ]
    for dy in range(7):
        for dx in range(7):
            if 0 <= y+dy < SIZE and 0 <= x+dx < SIZE:
                matrix[y+dy][x+dx] = pattern[dy][dx]
                reserved[y+dy][x+dx] = True

def add_separator_for_finder(matrix, reserved, x, y):
    """
    Add the white separator (1-module border) around a finder pattern
    placed at (x,y) (which is 7×7).
    """
    for dy in range(-1, 8):
        for dx in range(-1, 8):
            rx = x + dx
            ry = y + dy
            # Skip if outside the matrix or if inside the finder pattern.
            if rx < 0 or rx >= SIZE or ry < 0 or ry >= SIZE:
                continue
            if 0 <= dx < 7 and 0 <= dy < 7:
                continue
            matrix[ry][rx] = 0
            reserved[ry][rx] = True

def add_finder_patterns(matrix, reserved):
    """Place the three finder patterns and their separators."""
    # Top-left
    add_finder_pattern(matrix, reserved, 0, 0)
    add_separator_for_finder(matrix, reserved, 0, 0)
    # Top-right
    add_finder_pattern(matrix, reserved, SIZE - 7, 0)
    add_separator_for_finder(matrix, reserved, SIZE - 7, 0)
    # Bottom-left
    add_finder_pattern(matrix, reserved, 0, SIZE - 7)
    add_separator_for_finder(matrix, reserved, 0, SIZE - 7)

def add_timing_patterns(matrix, reserved):
    """
    Draw horizontal and vertical timing patterns.
    (For simplicity, we fill any cell in row 6 or column 6 that is still empty.)
    """
    # Horizontal timing pattern (row 6)
    for x in range(SIZE):
        if matrix[6][x] is None:
            matrix[6][x] = (x % 2)
            reserved[6][x] = True
    # Vertical timing pattern (column 6)
    for y in range(SIZE):
        if matrix[y][6] is None:
            matrix[y][6] = (y % 2)
            reserved[y][6] = True

def add_dark_module(matrix, reserved):
    """
    Add the dark module.
    (For Version 1, the dark module is defined to be at row (4*version+9) (1-indexed)
     and column 8 (1-indexed); convert to 0-indexed.)
    """
    r = 4 * VERSION + 9 - 1
    c = 8 - 1
    if r < SIZE and c < SIZE:
        matrix[r][c] = 1
        reserved[r][c] = True

def add_format_info(matrix, reserved, mask):
    """
    Place the 15 format-information bits into the matrix.
    (For simplicity, we hardcode the value for error correction level L and mask 0.)
    If you choose a different mask, you’d need to compute the correct format string.
    """
    if mask != 0:
        raise NotImplementedError("Only mask 0 is implemented for format info.")
    # Hardcoded format string for (L, mask 0): "111011111000100"
    fmt = "111011111000100"
    # One copy: positions (see QR spec)
    fmt_coords = [
        (8,0), (8,1), (8,2), (8,3), (8,4), (8,5), (8,7), (8,8),
        (7,8), (5,8), (4,8), (3,8), (2,8), (1,8), (0,8)
    ]
    for i, (r, c) in enumerate(fmt_coords):
        bit = int(fmt[i])
        matrix[r][c] = bit
        reserved[r][c] = True
    # The mirror copy (for the other format info area)
    fmt_coords_mirror = [
        (SIZE-1,8), (SIZE-2,8), (SIZE-3,8), (SIZE-4,8),
        (SIZE-5,8), (SIZE-6,8), (SIZE-7,8),
        (8,SIZE-8), (8,SIZE-7), (8,SIZE-6), (8,SIZE-5),
        (8,SIZE-4), (8,SIZE-3), (8,SIZE-2), (8,SIZE-1)
    ]
    for i, (r, c) in enumerate(fmt_coords_mirror):
        # Only fill if not already reserved.
        if not reserved[r][c]:
            bit = int(fmt[i])
            matrix[r][c] = bit
            reserved[r][c] = True

def place_data_bits(matrix, reserved, data_bits, mask):
    """
    Place the data bits into the QR matrix in the standard “zig‐zag” pattern.
    (This routine skips cells already marked as function modules.)
    The mask is applied “on the fly” – for mask 0, invert the bit if (r+c) is even.
    """
    bit_index = 0
    col = SIZE - 1
    direction = -1  # -1 means moving upward; 1 means moving downward.
    while col > 0:
        if col == 6:  # Skip the entire column 6 (timing pattern).
            col -= 1
        if direction == -1:
            rows = range(SIZE-1, -1, -1)
        else:
            rows = range(SIZE)
        for r in rows:
            for c in [col, col-1]:
                if reserved[r][c]:
                    continue
                if bit_index < len(data_bits):
                    bit = data_bits[bit_index]
                    # For mask 0: if (r+c) is even, flip the bit.
                    if mask == 0 and ((r + c) % 2 == 0):
                        bit ^= 1
                    matrix[r][c] = bit
                    bit_index += 1
                else:
                    # If no data remains, pad with 0.
                    matrix[r][c] = 0
        col -= 2
        direction = -direction

def generate_qr(data, mask=0):
    """
    Given an input string, generate a QR Code matrix (a 2D list of 0s and 1s).
    This routine encodes the data, computes error correction, and lays out the QR code.
    """
    # Step 1. Create the final message bits.
    final_message = create_final_message(data)
    data_bits = get_data_bit_list(final_message)

    # Step 2. Create an empty matrix and reserved mask.
    matrix, reserved = create_empty_matrix()

    # Step 3. Place function patterns.
    add_finder_patterns(matrix, reserved)
    add_timing_patterns(matrix, reserved)
    add_dark_module(matrix, reserved)
    add_format_info(matrix, reserved, mask)

    # Step 4. Place the data bits.
    place_data_bits(matrix, reserved, data_bits, mask)

    return matrix

# -------------------------------------
# Rendering the QR Code to an image
# -------------------------------------
def render_qr(matrix, scale=10, border=4):
    """
    Render the QR matrix to a PIL image.
      - scale: pixel size of each module
      - border: number of modules to leave as a white border around the QR code
    """
    img_size = (SIZE + 2 * border) * scale
    img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(img)
    for r in range(SIZE):
        for c in range(SIZE):
            if matrix[r][c] == 1:
                x0 = (c + border) * scale
                y0 = (r + border) * scale
                draw.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill="black")
    return img

# -------------------------------------
# Main: use from the command line
# -------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python qrgen.py 'your text' output.png")
        sys.exit(1)
    text = sys.argv[1]
    outfile = sys.argv[2]
    try:
        matrix = generate_qr(text, mask=0)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
    img = render_qr(matrix)
    img.save(outfile)
    print("QR Code saved to", outfile)