import re
import sys
from math import ceil

def check_power_of_two(x):
    i = 0
    while True:
        power = 2 ** i
        if power == x:
            return  # Found a match, simply return (pass)
        if power > x:
            raise ValueError(f"{x} is not a power of 2")
        i += 1

def parse_mermaid(lines):
    """
    Parse the Mermaid-like syntax to extract the title and field definitions.
    """
    title = None
    in_yaml = False
    fields = []

    for line in lines:
        line = line.strip()
        # Toggle YAML front matter boundaries.
        if line == "---":
            in_yaml = not in_yaml
            continue

        # Process YAML front matter.
        if in_yaml:
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"')
            continue

        if not line or ":" not in line:
            continue

        m = re.match(r'(\d+(?:-\d+)?):\s*"(.*)"', line)
        if m:
            range_str = m.group(1)
            label = m.group(2)
            if '-' in range_str:
                start, end = map(int, range_str.split('-'))
            else:
                start = end = int(range_str)
            fields.append((start, end, label))
    return title, fields

def generate_svg(title, fields, scale=10, height=40, row_spacing=0,
                 margin_x=30, margin_top=60, margin_bottom=30, padding=4):
    """
    Generate an SVG string for a multi-row packet diagram.
    """
    # Determine total bits.
    max_bit = max(end for _, end, _ in fields)
    total_bits = max_bit + 1
    check_power_of_two(total_bits)

    # Determine the maximum field width.
    max_field_width = max(end - start + 1 for start, end, _ in fields)

    # Choose bits_per_row as the smallest power of two >= max_field_width that divides total_bits.
    bits_per_row_candidate = 1 << (max_field_width - 1).bit_length()
    while total_bits % bits_per_row_candidate != 0:
        bits_per_row_candidate //= 2
    bits_per_row = bits_per_row_candidate

    # Determine number of rows based on bits_per_row.
    num_rows = total_bits // bits_per_row

    total_width = bits_per_row * scale + 2 * margin_x
    total_height = margin_top + num_rows * (height + row_spacing) - row_spacing + margin_bottom

    svg_elements = []
    svg_header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_width}" height="{total_height}" '
        f'viewBox="0 0 {total_width} {total_height}">'
    )
    svg_elements.append(svg_header)

    # Title centered at the top.
    if title:
        svg_elements.append(
            f'<text x="{total_width/2}" y="{margin_top/2}" text-anchor="middle" '
            f'style="font-size:1em;font-weight:bold;fill:white;">{title}</text>'
        )

    # Organize fields by row.
    rows = []
    for row in range(num_rows):
        row_start = row * bits_per_row
        row_end = row_start + bits_per_row - 1
        row_fields = []
        for (start, end, label) in fields:
            # Check if field overlaps this row.
            if start <= row_end and end >= row_start:
                clipped_start = max(start, row_start)
                clipped_end = min(end, row_end)
                row_fields.append((clipped_start, clipped_end, label, start, end))
        rows.append((row_start, row_end, row_fields))

    drawn_fields = set()  # Track fields that have been labeled.

    # Draw rows and fields.
    for row_index, (row_start, row_end, row_fields) in enumerate(rows):
        y_offset = margin_top + row_index * (height + row_spacing)

        for (clipped_start, clipped_end, label, orig_start, orig_end) in row_fields:
            # Calculate positions and dimensions for each field.
            field_x = margin_x + (clipped_start - row_start) * scale
            field_width = (clipped_end - clipped_start + 1) * scale

            # Draw field rectangle with distinct border.
            svg_elements.append(
                f'<rect x="{field_x}" y="{y_offset}" width="{field_width}" height="{height}" '
                f'fill="lightblue" stroke="black" />'
            )

            # Place bit indicators inside fields.
            marker_y = y_offset + padding
            if clipped_end == clipped_start:
                # Single-bit field: center marker at top.
                marker_x = field_x + field_width/2
                svg_elements.append(
                    f'<text x="{marker_x}" y="{marker_y}" text-anchor="middle" '
                    f'dominant-baseline="hanging" style="font-size:0.7em;fill:white;">{clipped_start}</text>'
                )
            else:
                # Multi-bit field: markers at top-left and top-right.
                left_marker_x = field_x + padding
                right_marker_x = field_x + field_width - padding
                svg_elements.append(
                    f'<text x="{left_marker_x}" y="{marker_y}" text-anchor="start" '
                    f'dominant-baseline="hanging" style="font-size:0.7em;fill:white;">{clipped_start}</text>'
                )
                svg_elements.append(
                    f'<text x="{right_marker_x}" y="{marker_y}" text-anchor="end" '
                    f'dominant-baseline="hanging" style="font-size:0.7em;fill:white;">{clipped_end}</text>'
                )

            # Center label within rectangle only for the first segment of a field.
            if (orig_start, orig_end) not in drawn_fields:
                text_x = field_x + field_width/2
                text_y = y_offset + height/2
                svg_elements.append(
                    f'<text x="{text_x}" y="{text_y}" text-anchor="middle" '
                    f'dominant-baseline="middle" style="font-size:0.8em;fill:black;">{label}</text>'
                )
                drawn_fields.add((orig_start, orig_end))

    svg_elements.append('</svg>')
    return "\n".join(svg_elements)

def main():
    if len(sys.argv) < 3:
        print("Usage: python packet_svg_generator.py input_file output_file")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        with open(input_path, 'r') as infile:
            lines = infile.readlines()
    except IOError as e:
        print(f"Error reading {input_path}: {e}")
        sys.exit(1)

    title, fields = parse_mermaid(lines)
    svg_content = generate_svg(title, fields)

    try:
        with open(output_path, 'w') as outfile:
            outfile.write(svg_content)
        print(f"SVG diagram saved to {output_path}")
    except IOError as e:
        print(f"Error writing to {output_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
