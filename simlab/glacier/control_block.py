import textwrap

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from icecream import ic


class Box:
    def __init__(self, fig, edge_color, width, height):
        self.fig = fig
        self.edge_color = edge_color
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def draw(self):
        rect = patches.Rectangle((self.x, self.y), self.width, self.height, transform=self.fig.transFigure,
                                 linewidth=2, edgecolor=self.edge_color, facecolor='none')
        self.fig.patches.append(rect)

    def scale(self, factor):
        self.width *= factor
        self.height *= factor
        self.x *= factor
        self.y *= factor


class KeyValueBox(Box):
    def __init__(self, fig, edge_color, width, height, key='', value='', key_font_size=10, value_font_size=12,
                 key_color='black', value_color='green', key_weight='normal', value_weight='bold',
                 key_ha='left', key_va='top', value_ha='center', value_va='center', inside_margin=0.02):
        super().__init__(fig, edge_color, width, height)
        self.key = key
        self.value = value
        self.key_font_size = key_font_size
        self.value_font_size = value_font_size
        self.key_color = key_color
        self.value_color = value_color
        self.key_weight = key_weight
        self.value_weight = value_weight
        self.key_ha = key_ha
        self.key_va = key_va
        self.value_ha = value_ha
        self.value_va = value_va
        self.inside_margin = inside_margin

    def get_wrap_width(self, text, max_width, fontsize):
        avg_char_width = plt.rcParams['font.size'] * 0.6 * fontsize / 10
        ic(avg_char_width)  # Debugging: Check the average character width at the current font size
        ic(plt.rcParams['font.size'])  # Debugging: Check the current font size
        # Convert max_width from figure-relative to pixels
        fig_dpi = self.fig.dpi
        fig_width, _ = self.fig.get_size_inches()
        available_pixel_width = max_width * fig_width * fig_dpi
        ic(max_width, fig_width, fig_dpi, available_pixel_width)  # Debugging: Check the available pixel width
        max_chars_per_line = int(available_pixel_width / avg_char_width)
        return max_chars_per_line

        # for chars_per_line in range(len(text), 0, -1):
        #     wrapped_text = textwrap.fill(text, width=chars_per_line)
        #     temp_text = self.fig.text(0, 0, wrapped_text, fontsize=fontsize, transform=None)
        #     bbox = temp_text.get_window_extent(renderer=self.fig.canvas.get_renderer())
        #     temp_text.remove()
        #     if bbox.width <= max_pixel_width:
        #         return chars_per_line
        #
        # return 1

    def adjust_font_size(self, text, max_width_inches, fontsize, weight, min_font_size=3):
        # Convert max_width from inches to pixels
        fig_dpi = self.fig.dpi
        fig_width, _ = self.fig.get_size_inches()
        max_width_pixels = max_width_inches * fig_width * fig_dpi

        # Estimate the average character width in pixels at the current font size
        avg_char_width = plt.rcParams['font.size'] * 0.6 * fontsize / 10  # Adjusted for the fontsize
        estimated_width = len(text) * avg_char_width

        while estimated_width > max_width_pixels and fontsize > min_font_size:
            fontsize -= 1
            estimated_width = len(text) * plt.rcParams['font.size'] * 0.6 * fontsize / 10 * (
                1.2 if weight == 'bold' else 1.0)

        return fontsize

    def draw_text_within_box(self, text, x, y, max_width, ha, va, fontsize, weight, color):
        ic(text)  # Debugging: Check the text to be drawn
        ic(x, y)  # Debugging: Check the position where text will be drawn
        ic(max_width)  # Debugging: Check the maximum width allowed for the text

        # Calculate the maximum number of characters per line
        max_chars_per_line = self.get_wrap_width(text, max_width, fontsize)
        ic(max_chars_per_line)  # Debugging: Check calculated max chars per line

        # Wrap the text
        wrapped_text = textwrap.fill(text, width=max_chars_per_line)
        ic(wrapped_text)  # Debugging: Check the wrapped text

        # Draw the text
        self.fig.text(x, y, wrapped_text, transform=self.fig.transFigure, ha=ha, va=va,
                      fontsize=fontsize, weight=weight, color=color)

    def draw(self):
        super().draw()  # Draw the box itself

        # Key text positioning
        key_max_width = self.width - self.inside_margin
        key_fontsize = self.adjust_font_size(self.key, key_max_width, self.key_font_size, self.key_weight)
        key_x = self.x + self.inside_margin / 2  # Left aligned by default
        key_y = self.y + self.height - self.inside_margin / 2  # Top aligned by default

        self.draw_text_within_box(self.key, key_x, key_y,
                                  key_max_width, self.key_ha, self.key_va,
                                  key_fontsize, self.key_weight, self.key_color)

        # Value text positioning
        value_max_width = self.width - self.inside_margin
        value_fontsize = self.adjust_font_size(self.value, value_max_width, self.value_font_size, self.value_weight)
        value_x = self.x + self.width / 2  # Default center horizontally
        value_y = self.y + self.height / 2  # Default center vertically

        # Adjust position based on alignment settings
        if self.value_ha == 'left':
            value_x = self.x + self.inside_margin / 2
        elif self.value_ha == 'right':
            value_x = self.x + self.width - self.inside_margin / 2

        if self.value_va == 'top':
            value_y = self.y + self.height - self.inside_margin / 2
        elif self.value_va == 'bottom':
            value_y = self.y + self.inside_margin / 2

        self.draw_text_within_box(self.value, value_x, value_y,
                                  value_max_width, self.value_ha, self.value_va,
                                  value_fontsize, self.value_weight, self.value_color)

    def scale(self, factor):
        super().scale(factor)
        self.key_font_size *= factor
        self.value_font_size *= factor


class ControlBlock:
    def __init__(self, fig, grid_cols=3, grid_rows=3, start_x=0.0, start_y=0.0):
        self.fig = fig
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        self.start_x = start_x
        self.start_y = start_y
        self.boxes = []

    def add_box(self, box, col, row):
        box_width = box.width
        ic(box_width)
        box_height = box.height
        ic(box_height)
        box.x = self.start_x + col * box_width
        box.y = self.start_y + (self.grid_rows - row - 1) * box_height
        self.boxes.append(box)

    def scale(self, factor):
        for box in self.boxes:
            box.scale(factor)
            box.x = self.start_x + box.x * factor
            box.y = self.start_y + box.y * factor

    def draw(self):
        for box in self.boxes:
            box.draw()


if __name__ == '__main__':
    fig = plt.figure(figsize=(10, 8))

    # Create KeyValueBox objects
    box1 = KeyValueBox(fig, edge_color='black', width=0.2, height=0.1, key="Classification:", value="Unclassified",
                       key_ha='left', key_va='top', value_ha='center', value_va='center')
    box2 = KeyValueBox(fig, edge_color='black', width=0.2, height=0.1, key="Status:", value="Active", key_ha='left',
                       key_va='top', value_ha='center', value_va='center')
    box3 = KeyValueBox(fig, edge_color='black', width=0.2, height=0.1, key="Level:", value="High", key_ha='left',
                       key_va='top', value_ha='center', value_va='center')
    box4 = KeyValueBox(fig, edge_color='black', width=box3.width * 3, height=box1.height, key="Status:",
                       value="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident. Sunt in culpa qui officia deserunt mollit anim id est laborum.",
                       key_ha='left', key_va='top', value_ha='left', value_va='center')

    # Create ControlBlock and add KeyValueBoxes
    control_block = ControlBlock(fig, grid_rows=2, grid_cols=3, start_x=0, start_y=0)
    control_block.add_box(box1, row=0, col=0)
    control_block.add_box(box2, row=0, col=1)
    control_block.add_box(box3, row=0, col=2)
    control_block.add_box(box4, row=1, col=0)  # Spanning the entire row
    control_block.draw()

    #    fig.savefig('control_block.png', dpi=300)

    plt.show()
