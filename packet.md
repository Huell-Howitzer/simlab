import re
from math import ceil

def parse_mermaid(lines):
    title = None
    in_yaml = False
    fields = []

    for line in lines:
        line = line.strip()
        if line == "---":
            in_yaml = not in_yaml
            continue

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

def generate_svg(title, fields, bits_per_row=32, scale=10, height=40, row_spacing=0, 
                 margin_x=30, margin_top=60, margin_bottom=30, padding=4):
    max_bit = max(end for _, end, _ in fields)
    total_bits = max_bit + 1
    num_rows = ceil(total_bits / bits_per_row)

    total_width = bits_per_row * scale + 2 * margin_x
    total_height = margin_top + num_rows * height + margin_bottom

    svg_elements = []
    svg_header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_width}" height="{total_height}" '
        f'viewBox="0 0 {total_width} {total_height}">'
    )
    svg_elements.append(svg_header)

    if title:
        svg_elements.append(
            f'<text x="{total_width/2}" y="{margin_top/2}" text-anchor="middle" '
            f'style="font-size:1em;font-weight:bold;fill:black;">{title}</text>'
        )

    for row in range(num_rows):
        row_start = row * bits_per_row
        row_end = row_start + bits_per_row - 1
        y_offset = margin_top + row * height

        for (start, end, label) in fields:
            if start > row_end or end < row_start:
                continue  # skip if not in this row

            clipped_start = max(start, row_start)
            clipped_end = min(end, row_end)

            field_x = margin_x + (clipped_start - row_start) * scale
            field_width = (clipped_end - clipped_start + 1) * scale

            svg_elements.append(
                f'<rect x="{field_x}" y="{y_offset}" width="{field_width}" height="{height}" '
                f'fill="lightblue" stroke="black" stroke-width="1"/>'
            )

            # Determine font size: small for narrow fields, regular for wider
            bit_span = clipped_end - clipped_start + 1
            if bit_span <= 2:
                font_size = 0.4 * min(scale, height)
            else:
                font_size = 0.6 * min(scale, height)

            text_x = field_x + field_width/2
            text_y = y_offset + height/2
            svg_elements.append(
                f'<text x="{text_x}" y="{text_y}" text-anchor="middle" '
                f'dominant-baseline="middle" style="font-size:{font_size}px;fill:black;">{label}</text>'
            )

            # Add upper corner bit numbers if wide enough (> 2 bits)
            if bit_span > 2:
                corner_font_size = 0.4 * min(scale, height)
                svg_elements.append(
                    f'<text x="{field_x + padding}" y="{y_offset + padding + 2}" text-anchor="start" '
                    f'style="font-size:{corner_font_size}px;fill:black;">{clipped_start}</text>'
                )
                svg_elements.append(
                    f'<text x="{field_x + field_width - padding}" y="{y_offset + padding + 2}" text-anchor="end" '
                    f'style="font-size:{corner_font_size}px;fill:black;">{clipped_end}</text>'
                )

    svg_elements.append('</svg>')
    return "\n".join(svg_elements)

mermaid_input = """---
title: "TCP Packet"
---
packet-beta
0-15: "Source Port"
16-31: "Destination Port"
32-63: "Sequence Number"
64-95: "Acknowledgment Number"
96-99: "Data Offset"
100-105: "Reserved"
106: "URG"
107: "ACK"
108: "PSH"
109: "RST"
110: "SYN"
111: "FIN"
112-127: "Window"
128-143: "Checksum"
144-159: "Urgent Pointer"
160-191: "(Options and Padding)"
192-255: "Data (variable length)"
"""

input_lines = mermaid_input.strip().splitlines()
title, fields = parse_mermaid(input_lines)
svg_output = generate_svg(title, fields)

output_path = '/mnt/data/tcp_packet_diagram_small_font_narrow.svg'
with open(output_path, "w", encoding="utf-8") as f:
    f.write(svg_output)

output_path