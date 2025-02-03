#!/usr/bin/env python3
"""
Extended QR Code Generator in Python (up to Version 40).

Features:
  • Supports Version 1, 2, and 40 (for demonstration – normally versions 1–40).
  • Automatic encoding mode selection (numeric, alphanumeric, or byte).
  • Automatic version selection if the version parameter is "auto" (choosing the smallest version that fits).
  • Supports Error Correction Levels L, M, Q, and H.
  • Dynamic mask selection (if mask is not provided).
  • Computed format information via a BCH algorithm.
  • Placement of finder patterns, alignment patterns (using a lookup table), timing patterns, and dark module.
  • Reed–Solomon error correction (using GF(256) arithmetic).
  • Rendering output as PNG (via Pillow), SVG, or ASCII text.
  
Usage:
  python qrgen.py "your text" output_file [version: auto, 1, 2, or 40] [EC level: L, M, Q, H] [mask (0-7)]

If the version is "auto" (or omitted) the generator selects the smallest supported version that fits the data.
The output type is determined by the output file’s extension:
  • .png → PNG image (via Pillow)
  • .svg → SVG vector image
  • .txt → ASCII text output
"""

import sys
import os
from PIL import Image, ImageDraw

# -------------------------------------------------------------------
# QR Code version parameters.
# For demonstration, we include only versions 1, 2, and 40.
# For each version we store:
#   • size: modules per side,
#   • For each error correction level: (data codewords, ECC codewords)
# (These values are taken from the QR Code standard for byte mode.)
# -------------------------------------------------------------------
QR_VERSIONS = {
    1: {
        'size': 21,
        'L': (19, 7),
        'M': (16, 10),
        'Q': (13, 12),
        'H': (9, 17)
    },
    2: {
        'size': 25,
        'L': (34, 10),
        'M': (28, 16),
        'Q': (22, 22),
        'H': (16, 28)
    },
    40: {
        'size': 177,
        'L': (2953, 753),
        'M': (2331, 1375),
        'Q': (1663, 2043),
        'H': (1273, 2433)
    }
}

# Global parameters (default values; these will be updated below)
QR_VERSION = 1
QR_SIZE = QR_VERSIONS[QR_VERSION]['size']
QR_DATA_CODEWORDS, QR_ECC_CODEWORDS = QR_VERSIONS[QR_VERSION]['L']
QR_EC_LEVEL = 'L'

# -------------------------------------------------------------------
# Alignment Pattern Locations (for versions ≥2).
# For version 1 there are none.
# For version 2 the centers are [6, 18];
# For version 40 the standard specifies: [6, 30, 58, 86, 114, 142, 170].
# (A full implementation would include entries for all versions.)
# -------------------------------------------------------------------
ALIGNMENT_PATTERN_LOCATIONS = {
    1: [],
    2: [6, 18],
    40: [6, 30, 58, 86, 114, 142, 170]
}

# -------------------------------------------------------------------
# GF(256) arithmetic (using primitive polynomial 0x11d)
# Precompute exponent and logarithm tables.
# -------------------------------------------------------------------
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
    if a == 0 or b == 0:
        return 0
    return EXP_TABLE[(LOG_TABLE[a] + LOG_TABLE[b]) % 255]

def gf_poly_mul(p, q):
    result = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        for j in range(len(q)):
            result[i+j] ^= gf_mul(p[i], q[j])
    return result

def rs_generator_poly(nsym):
    g = [1]
    for i in range(nsym):
        g = gf_poly_mul(g, [1, EXP_TABLE[i]])
    return g

# -------------------------------------------------------------------
# Encoding routines: automatic mode selection among numeric, alphanumeric, and byte.
# -------------------------------------------------------------------
def choose_mode(data):
    if all(ch in "0123456789" for ch in data):
        return "numeric"
    allowed = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
    if all(ch in allowed for ch in data):
        return "alphanumeric"
    return "byte"

def encode_numeric(data, count_indicator_bits):
    bits = "0001"  # Mode indicator for numeric.
    bits += format(len(data), "0{}b".format(count_indicator_bits))
    i = 0
    while i < len(data):
        group = data[i:i+3]
        if len(group) == 3:
            bits += format(int(group), "010b")
        elif len(group) == 2:
            bits += format(int(group), "07b")
        else:
            bits += format(int(group), "04b")
        i += 3
    return bits

def encode_alphanumeric(data, count_indicator_bits):
    bits = "0010"  # Mode indicator for alphanumeric.
    bits += format(len(data), "0{}b".format(count_indicator_bits))
    table = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
    i = 0
    while i < len(data):
        if i + 1 < len(data):
            v = table.index(data[i]) * 45 + table.index(data[i+1])
            bits += format(v, "011b")
            i += 2
        else:
            bits += format(table.index(data[i]), "06b")
            i += 1
    return bits

def encode_byte(data, count_indicator_bits):
    bits = "0100"  # Mode indicator for byte.
    bits += format(len(data), "0{}b".format(count_indicator_bits))
    for ch in data:
        bits += format(ord(ch), "08b")
    return bits

def encode_data_all(data):
    mode = choose_mode(data)
    # The length (character count) indicator bit–length depends on the mode and version.
    if mode == "numeric":
        count_bits = 10 if QR_VERSION == 1 else 12
        bits = encode_numeric(data, count_bits)
    elif mode == "alphanumeric":
        count_bits = 9 if QR_VERSION == 1 else 11
        bits = encode_alphanumeric(data, count_bits)
    else:
        count_bits = 8  # For byte mode the indicator is always 8 bits (for versions 1–9; larger versions use more, but for simplicity we use 8)
        bits = encode_byte(data, count_bits)
    available = QR_DATA_CODEWORDS * 8
    if len(bits) > available:
        raise ValueError("Data too long for version {} EC level {} in {} mode."
                         .format(QR_VERSION, QR_EC_LEVEL, mode))
    terminator_len = min(4, available - len(bits))
    bits += "0" * terminator_len
    while len(bits) % 8 != 0:
        bits += "0"
    codewords = []
    for i in range(0, len(bits), 8):
        codewords.append(int(bits[i:i+8], 2))
    pad_bytes = [0xEC, 0x11]
    pad_index = 0
    while len(codewords) < QR_DATA_CODEWORDS:
        codewords.append(pad_bytes[pad_index % 2])
        pad_index += 1
    return codewords

def create_final_message(data):
    data_codewords = encode_data_all(data)
    ecc_codewords = calculate_ecc(data_codewords, QR_ECC_CODEWORDS)
    return data_codewords + ecc_codewords

def get_data_bit_list(final_message):
    bits = ""
    for cw in final_message:
        bits += format(cw, "08b")
    return [int(b) for b in bits]

# -------------------------------------------------------------------
# Automatic version selection: choose the smallest supported version that fits.
# Here our supported versions are 1, 2, and 40.
# -------------------------------------------------------------------
def auto_select_version(data, ec_level):
    global QR_VERSION, QR_SIZE, QR_DATA_CODEWORDS, QR_ECC_CODEWORDS, QR_EC_LEVEL
    QR_EC_LEVEL = ec_level
    for ver in sorted(QR_VERSIONS.keys()):
        try:
            QR_VERSION = ver
            QR_SIZE = QR_VERSIONS[ver]['size']
            if ec_level not in QR_VERSIONS[ver]:
                continue
            QR_DATA_CODEWORDS, QR_ECC_CODEWORDS = QR_VERSIONS[ver][ec_level]
            _ = encode_data_all(data)
            return ver
        except ValueError:
            continue
    raise ValueError("Data too long to fit in supported versions.")

# -------------------------------------------------------------------
# Matrix construction functions.
# -------------------------------------------------------------------
def create_empty_matrix():
    matrix = [[None for _ in range(QR_SIZE)] for _ in range(QR_SIZE)]
    reserved = [[False for _ in range(QR_SIZE)] for _ in range(QR_SIZE)]
    return matrix, reserved

def add_finder_pattern(matrix, reserved, x, y):
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
            if 0 <= y+dy < QR_SIZE and 0 <= x+dx < QR_SIZE:
                matrix[y+dy][x+dx] = pattern[dy][dx]
                reserved[y+dy][x+dx] = True

def add_separator_for_finder(matrix, reserved, x, y):
    for dy in range(-1, 8):
        for dx in range(-1, 8):
            rx = x + dx
            ry = y + dy
            if rx < 0 or rx >= QR_SIZE or ry < 0 or ry >= QR_SIZE:
                continue
            if 0 <= dx < 7 and 0 <= dy < 7:
                continue
            matrix[ry][rx] = 0
            reserved[ry][rx] = True

def add_finder_patterns(matrix, reserved):
    add_finder_pattern(matrix, reserved, 0, 0)
    add_separator_for_finder(matrix, reserved, 0, 0)
    add_finder_pattern(matrix, reserved, QR_SIZE - 7, 0)
    add_separator_for_finder(matrix, reserved, QR_SIZE - 7, 0)
    add_finder_pattern(matrix, reserved, 0, QR_SIZE - 7)
    add_separator_for_finder(matrix, reserved, 0, QR_SIZE - 7)

def add_alignment_pattern(matrix, reserved, center_r, center_c):
    pattern = [
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,0,1,0,1],
        [1,0,0,0,1],
        [1,1,1,1,1],
    ]
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            r = center_r + dy
            c = center_c + dx
            if 0 <= r < QR_SIZE and 0 <= c < QR_SIZE:
                matrix[r][c] = pattern[dy+2][dx+2]
                reserved[r][c] = True

def add_alignment_patterns(matrix, reserved):
    if QR_VERSION < 2:
        return
    centers = ALIGNMENT_PATTERN_LOCATIONS.get(QR_VERSION, [])
    for r in centers:
        for c in centers:
            # Skip positions that overlap with finder patterns.
            if (r == 6 and c == 6) or (r == 6 and c == QR_SIZE - 7) or (r == QR_SIZE - 7 and c == 6):
                continue
            add_alignment_pattern(matrix, reserved, r, c)

def add_timing_patterns(matrix, reserved):
    for x in range(QR_SIZE):
        if matrix[6][x] is None:
            matrix[6][x] = (x % 2)
            reserved[6][x] = True
    for y in range(QR_SIZE):
        if matrix[y][6] is None:
            matrix[y][6] = (y % 2)
            reserved[y][6] = True

def add_dark_module(matrix, reserved):
    r = 4 * QR_VERSION + 9 - 1
    c = 8 - 1
    if r < QR_SIZE and c < QR_SIZE:
        matrix[r][c] = 1
        reserved[r][c] = True

def compute_format_info(mask, ec_level):
    mapping = {'L': 0b01, 'M': 0b00, 'Q': 0b11, 'H': 0b10}
    ec_bits = mapping[ec_level]
    format_data = (ec_bits << 3) | mask
    g = 0x537
    code = format_data << 10
    for i in range(14, 9, -1):
        if code & (1 << i):
            code ^= g << (i - 10)
    format_info = ((format_data << 10) | code) ^ 0x5412
    return format(format_info, '015b')

def add_format_info(matrix, reserved, mask, ec_level):
    fmt = compute_format_info(mask, ec_level)
    fmt_coords = [
        (8,0), (8,1), (8,2), (8,3), (8,4), (8,5), (8,7), (8,8),
        (7,8), (5,8), (4,8), (3,8), (2,8), (1,8), (0,8)
    ]
    for i, (r, c) in enumerate(fmt_coords):
        matrix[r][c] = int(fmt[i])
        reserved[r][c] = True
    fmt_coords_mirror = [
        (QR_SIZE-1,8), (QR_SIZE-2,8), (QR_SIZE-3,8), (QR_SIZE-4,8),
        (QR_SIZE-5,8), (QR_SIZE-6,8), (QR_SIZE-7,8),
        (8,QR_SIZE-8), (8,QR_SIZE-7), (8,QR_SIZE-6), (8,QR_SIZE-5),
        (8,QR_SIZE-4), (8,QR_SIZE-3), (8,QR_SIZE-2), (8,QR_SIZE-1)
    ]
    for i, (r, c) in enumerate(fmt_coords_mirror):
        if not reserved[r][c]:
            matrix[r][c] = int(fmt[i])
            reserved[r][c] = True

def mask_condition(r, c, mask):
    if mask == 0:
        return (r + c) % 2 == 0
    elif mask == 1:
        return (r % 2) == 0
    elif mask == 2:
        return (c % 3) == 0
    elif mask == 3:
        return (r + c) % 3 == 0
    elif mask == 4:
        return ((r // 2) + (c // 3)) % 2 == 0
    elif mask == 5:
        return (r * c) % 2 + (r * c) % 3 == 0
    elif mask == 6:
        return ((r * c) % 2 + (r * c) % 3) % 2 == 0
    elif mask == 7:
        return ((r + c) % 2 + (r * c) % 3) % 2 == 0
    else:
        return False

def place_data_bits(matrix, reserved, data_bits, mask):
    bit_index = 0
    col = QR_SIZE - 1
    direction = -1
    while col > 0:
        if col == 6:
            col -= 1
        rows = range(QR_SIZE-1, -1, -1) if direction == -1 else range(QR_SIZE)
        for r in rows:
            for c in [col, col-1]:
                if reserved[r][c]:
                    continue
                if bit_index < len(data_bits):
                    bit = data_bits[bit_index]
                    if mask_condition(r, c, mask):
                        bit ^= 1
                    matrix[r][c] = bit
                    bit_index += 1
                else:
                    matrix[r][c] = 0
        col -= 2
        direction = -direction

def compute_penalty(matrix):
    penalty = 0
    for row in matrix:
        run_length = 1
        for i in range(1, QR_SIZE):
            if row[i] == row[i-1]:
                run_length += 1
            else:
                if run_length >= 5:
                    penalty += 3 + (run_length - 5)
                run_length = 1
        if run_length >= 5:
            penalty += 3 + (run_length - 5)
    for c in range(QR_SIZE):
        run_length = 1
        for r in range(1, QR_SIZE):
            if matrix[r][c] == matrix[r-1][c]:
                run_length += 1
            else:
                if run_length >= 5:
                    penalty += 3 + (run_length - 5)
                run_length = 1
        if run_length >= 5:
            penalty += 3 + (run_length - 5)
    for r in range(QR_SIZE - 1):
        for c in range(QR_SIZE - 1):
            if matrix[r][c] == matrix[r][c+1] == matrix[r+1][c] == matrix[r+1][c+1]:
                penalty += 3
    for r in range(QR_SIZE):
        row = matrix[r]
        for c in range(QR_SIZE - 6):
            if row[c:c+7] == [1,0,1,1,1,0,1]:
                if (c >= 4 and row[c-4:c] == [0,0,0,0]) or (c <= QR_SIZE - 11 and row[c+7:c+11] == [0,0,0,0]):
                    penalty += 40
    for c in range(QR_SIZE):
        col = [matrix[r][c] for r in range(QR_SIZE)]
        for r in range(QR_SIZE - 6):
            if col[r:r+7] == [1,0,1,1,1,0,1]:
                if (r >= 4 and col[r-4:r] == [0,0,0,0]) or (r <= QR_SIZE - 11 and col[r+7:r+11] == [0,0,0,0]):
                    penalty += 40
    dark_count = sum(row.count(1) for row in matrix)
    total = QR_SIZE * QR_SIZE
    percent = (dark_count * 100) // total
    deviation = abs(percent - 50) // 5
    penalty += deviation * 10
    return penalty

def calculate_ecc(data_codewords, nsym):
    gen = rs_generator_poly(nsym)
    msg = data_codewords + [0] * nsym
    for i in range(len(data_codewords)):
        coef = msg[i]
        if coef != 0:
            for j in range(len(gen)):
                msg[i+j] ^= gf_mul(gen[j], coef)
    return msg[-nsym:]

def _generate_qr(data, ec_level, mask):
    final_message = create_final_message(data)
    data_bits = get_data_bit_list(final_message)
    matrix, reserved = create_empty_matrix()
    add_finder_patterns(matrix, reserved)
    add_alignment_patterns(matrix, reserved)
    add_timing_patterns(matrix, reserved)
    add_dark_module(matrix, reserved)
    add_format_info(matrix, reserved, mask, ec_level)
    place_data_bits(matrix, reserved, data_bits, mask)
    return matrix

def generate_qr(data, ec_level='L', mask=None):
    if mask is None:
        best_mask = None
        best_matrix = None
        best_penalty = None
        for m in range(8):
            matrix = _generate_qr(data, ec_level, m)
            penalty = compute_penalty(matrix)
            if best_penalty is None or penalty < best_penalty:
                best_penalty = penalty
                best_mask = m
                best_matrix = matrix
        print("Selected mask:", best_mask, "with penalty", best_penalty)
        return best_matrix
    else:
        return _generate_qr(data, ec_level, mask)

# -------------------------------------------------------------------
# Rendering functions.
# -------------------------------------------------------------------
def render_qr_png(matrix, scale=10, border=4):
    img_size = (QR_SIZE + 2 * border) * scale
    img = Image.new("RGB", (img_size, img_size), "white")
    draw = ImageDraw.Draw(img)
    for r in range(QR_SIZE):
        for c in range(QR_SIZE):
            if matrix[r][c] == 1:
                x0 = (c + border) * scale
                y0 = (r + border) * scale
                draw.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill="black")
    return img

def render_qr_svg(matrix, scale=10, border=4):
    total_size = (QR_SIZE + 2 * border) * scale
    svg = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<svg xmlns="http://www.w3.org/2000/svg" version="1.1"',
           f' width="{total_size}" height="{total_size}" viewBox="0 0 {total_size} {total_size}">',
           '<rect width="100%" height="100%" fill="white"/>']
    for r in range(QR_SIZE):
        for c in range(QR_SIZE):
            if matrix[r][c] == 1:
                x = (c + border) * scale
                y = (r + border) * scale
                svg.append(f'<rect x="{x}" y="{y}" width="{scale}" height="{scale}" fill="black"/>')
    svg.append('</svg>')
    return "\n".join(svg)

def render_qr_ascii(matrix, border=2):
    output = []
    blank_line = " " * ((QR_SIZE + 2 * border) * 2)
    for _ in range(border):
        output.append(blank_line)
    for r in range(QR_SIZE):
        line = " " * (border * 2)
        for c in range(QR_SIZE):
            line += "██" if matrix[r][c] == 1 else "  "
        line += " " * (border * 2)
        output.append(line)
    for _ in range(border):
        output.append(blank_line)
    return "\n".join(output)

# -------------------------------------------------------------------
# Main: command-line argument parsing, version selection, rendering, and output.
# -------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python qrgen.py 'your text' output_file [version: auto, 1, 2, or 40] [EC level: L, M, Q, H] [mask (0-7)]")
        sys.exit(1)
    text = sys.argv[1]
    outfile = sys.argv[2]
    
    ext = os.path.splitext(outfile)[1].lower()
    output_format = "png"
    if ext == ".svg":
        output_format = "svg"
    elif ext == ".txt":
        output_format = "ascii"
    
    version_arg = sys.argv[3] if len(sys.argv) >= 4 else "auto"
    if version_arg.lower() == "auto":
        auto_version = True
    else:
        auto_version = False
        try:
            version_val = int(version_arg)
            if version_val not in QR_VERSIONS:
                print("Supported versions in this demo are: " + ", ".join(str(v) for v in QR_VERSIONS.keys()))
                sys.exit(1)
            QR_VERSION = version_val
        except ValueError:
            print("Invalid version. Use 'auto', 1, 2, or 40.")
            sys.exit(1)
    
    QR_EC_LEVEL = sys.argv[4].upper() if len(sys.argv) >= 5 else "L"
    if QR_EC_LEVEL not in ["L", "M", "Q", "H"]:
        print("Invalid error correction level. Choose L, M, Q, or H.")
        sys.exit(1)
    
    if auto_version:
        try:
            chosen_version = auto_select_version(text, QR_EC_LEVEL)
            print("Auto-selected version:", chosen_version)
        except ValueError as e:
            print("Error:", e)
            sys.exit(1)
    else:
        QR_SIZE = QR_VERSIONS[QR_VERSION]['size']
        if QR_EC_LEVEL not in QR_VERSIONS[QR_VERSION]:
            print(f"Error: Version {QR_VERSION} does not support EC level {QR_EC_LEVEL}.")
            sys.exit(1)
        QR_DATA_CODEWORDS, QR_ECC_CODEWORDS = QR_VERSIONS[QR_VERSION][QR_EC_LEVEL]
    
    mask = None
    if len(sys.argv) >= 6:
        try:
            mask = int(sys.argv[5])
            if mask < 0 or mask > 7:
                raise ValueError()
        except ValueError:
            print("Mask must be an integer from 0 to 7.")
            sys.exit(1)
    
    try:
        matrix = generate_qr(text, QR_EC_LEVEL, mask)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
    
    if output_format == "png":
        img = render_qr_png(matrix)
        img.save(outfile)
        print("QR Code saved to", outfile)
    elif output_format == "svg":
        svg_data = render_qr_svg(matrix)
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(svg_data)
        print("SVG QR Code saved to", outfile)
    elif output_format == "ascii":
        ascii_data = render_qr_ascii(matrix)
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(ascii_data)
        print("ASCII QR Code saved to", outfile)