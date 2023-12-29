import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
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
                 key_ha='left', key_va='top', value_ha='center', value_va='center', inside_margin=0.01):
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

    def calculate_horizontal_position(self, ha):
        # Simplified logic for horizontal position
        if ha == 'left':
            return self.x + self.inside_margin
        elif ha == 'center':
            return self.x + self.width / 2
        elif ha == 'right':
            return self.x + self.width - self.inside_margin

    def calculate_vertical_position(self, va):
        # Simplified logic for vertical position
        if va == 'top':
            return self.y + self.height - self.inside_margin
        elif va == 'center':
            return self.y + self.height / 2
        elif va == 'bottom':
            return self.y + self.inside_margin

    def get_text_height(self, text, fontsize):
        """Calculate the height of the given text with the spe1ified font size."""
        temp_text = self.fig.text(0, 0, text, fontsize=fontsize, transform=None)
        bbox = temp_text.get_window_extent(renderer=self.fig.canvas.get_renderer())
        temp_text.remove()
        ic(bbox.height)
        return bbox.height

    def adjust_font_size_for_height(self, text, max_height_pixels, fontsize, min_font_size=3):
        """Adjust font size based on the available height in pixels."""
        text_height = self.get_text_height(text, fontsize)

        while text_height > max_height_pixels and fontsize > min_font_size:
            fontsize -= 1
            text_height = self.get_text_height(text, fontsize)

        return max(fontsize, min_font_size)

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

    def calculate_text_position(self, text, fontsize, ha, va):
        text_width, text_height = self.get_text_dimensions(text, fontsize)
        x, y = self.x, self.y  # Default positions

        # Adjust horizontal position
        if ha == 'center':
            x += (self.width - text_width) / 2
        elif ha == 'right':
            x += self.width - text_width - self.inside_margin

        # Adjust vertical position
        if va == 'center':
            y += (self.height - text_height) / 2
        elif va == 'bottom':
            y += self.height - text_height - self.inside_margin

        return x, y

    def get_text_dimensions(self, text, fontsize):
        """Calculate the width and height of the text."""
        temp_text = self.fig.text(0, 0, text, fontsize=fontsize, transform=None)
        bbox = temp_text.get_window_extent(renderer=self.fig.canvas.get_renderer())
        temp_text.remove()
        return bbox.width, bbox.height

    def draw_text_within_box(self, text, ha, va, fontsize, color, weight):
        # Adjust the font size based on the width of the box
        max_width = self.width - 2 * self.inside_margin  # Consider margins
        fontsize = self.adjust_font_size(text, max_width, fontsize, weight)

        # Calculate the text position
        x = self.calculate_horizontal_position(ha)
        y = self.calculate_vertical_position(va)

        # Draw the text
        self.fig.text(x, y, text, ha=ha, va=va, fontsize=fontsize, color=color, weight=weight)

        # max_chars_per_line = self.get_wrap_width(text, max_width, fontsize)
        # wrapped_text = textwrap.fill(text, width=max_chars_per_line)
        #
        # fig_height = self.fig.get_size_inches()[1] * self.fig.dpi
        # max_height_pixels = self.height * fig_height - self.inside_margin * fig_height
        # fontsize = self.adjust_font_size_for_height(wrapped_text, max_height_pixels, fontsize)
        #
        # # Calculate text height
        # text_height = self.get_text_height(wrapped_text, fontsize)
        #
        # # Adjust y position based on font size and vertical alignment
        # adjusted_y = y  # Initialize with the original y
        # if va == 'top':
        #     adjusted_y = y + self.height - self.inside_margin / 2 - text_height
        # elif va == 'center':
        #     adjusted_y = y + (self.height / 2) - (text_height / 2)
        # elif va == 'bottom':
        #     adjusted_y = y + self.inside_margin / 2
        #
        # # Mark the adjusted position
        # plt.scatter(x, adjusted_y, c='red')  # Red dot marker at the adjusted position
        #
        # # Draw the text
        # self.fig.text(x, adjusted_y, wrapped_text, ha=ha, va=va, fontsize=fontsize, weight=weight, color=color)

    def draw(self):
        super().draw()  # Draw the box itself

        # Draw key text
        self.draw_text_within_box(self.key, self.key_ha, self.key_va, self.key_font_size, self.key_color,
                                  self.key_weight)

        # Draw value text
        self.draw_text_within_box(self.value, self.value_ha, self.value_va, self.value_font_size, self.value_color,
                                  self.value_weight)

    def scale(self, factor):
        super().scale(factor)
        self.key_font_size *= factor
        self.value_font_size *= factor
        self.inside_margin *= factor
        self.height *= factor
        self.width *= factor
        self.x *= factor
        self.y *= factor


class ControlBlock:
    def __init__(self, fig, grid_cols=3, grid_rows=3, start_x=0.0, start_y=0.0):
        self.fig = fig
        self.grid_cols = grid_cols
        self.grid_rows = grid_rows
        self.start_x = start_x
        self.start_y = start_y
        self.boxes = []

    def add_box(self, box, col, row):
        # Calculate the box's position within the grid
        box_width = box.width
        box_height = box.height
        box.x = self.start_x + col * box_width
        box.y = self.start_y + (self.grid_rows - row - 1) * box_height
        self.boxes.append(box)
        ic(f"Added box at x={box.x}, y={box.y}, width={box_width}, height={box_height}")

    def scale(self, factor):
        for box in self.boxes:
            box.scale(factor)
            ic(f"Scaled box to x={box.x}, y={box.y}, width={box.width}, height={box.height}")

    def draw(self):
        for box in self.boxes:
            box.draw()
            ic(f"Drew box at x={box.x}, y={box.y}, width={box.width}, height={box.height}")

    def get_size(self):
        height = 0
        width = 0
        for box in self.boxes:
            height = max(height, box.y + box.height)
            width = max(width, box.x + box.width)
        return width, height

    def get_position(self):
        x0 = self.start_x
        y0 = self.start_y
        block_size = self.get_size()
        x1 = x0 + block_size[0]
        y1 = y0 + block_size[1]
        return x0, y0, x1, y1

    def check_overlap(self, gap=0.025):
        # Get the position bounds of the control block and the plot
        control_block_position = self.get_position()
        plot_position = self.fig.axes[0].get_position().bounds

        # Adjust plot_position bounds to include the gap
        adjusted_plot_position = (
            plot_position[0] - gap,  # left
            plot_position[1] - gap,  # bottom
            plot_position[0] + plot_position[2] + gap,  # right
            plot_position[1] + plot_position[3] + gap  # top
        )

        # Check for overlap considering the gap
        overlap = not (control_block_position[2] < adjusted_plot_position[0] or
                       control_block_position[0] > adjusted_plot_position[2] or
                       control_block_position[3] < adjusted_plot_position[1] or
                       control_block_position[1] > adjusted_plot_position[3])

        return overlap


if __name__ == '__main__':

    def adjust_plot_size(fig, ax, control_block):
        plot_position = ax.get_position()
        control_block_position = control_block.get_position()

        # Calculate the new left boundary for the plot
        if control_block_position[2] > plot_position.x0:  # If control block overlaps with the plot
            shift = control_block_position[2] - plot_position.x0  # Calculate how much to shift
            new_x0 = plot_position.x0 + shift  # Shift the plot to the right

            # Adjust plot position
            ax.set_position([new_x0, plot_position.y0, plot_position.width, plot_position.height])


    def adjust_plot_vertical_position(fig, ax, control_block):
        plot_position = ax.get_position()
        control_block_position = control_block.get_position()

        # Check if the control block overlaps or is too close to the plot vertically
        min_distance = 0.2  # Minimum distance between plot and control block, in normalized figure units
        if control_block_position[3] + min_distance > plot_position.y0:
            # Calculate the new vertical position for the plot
            new_height = plot_position.y0 - (control_block_position[3] + min_distance)
            new_y0 = control_block_position[3] + min_distance

            # Check if the new height is positive (to ensure the plot remains visible)
            if new_height > 0:
                ax.set_position([plot_position.x0, new_y0, plot_position.width, new_height])
            else:
                print("Warning: Control block is too large, reducing plot height significantly!")


    x = np.random.uniform(low=0, high=100, size=100)
    y = np.random.uniform(low=0, high=100, size=100)
    fig, ax = plt.subplots(figsize=(8.5, 11))  # Create a figure and an axes.

    # Plotting using the Axes instance
    ax.scatter(x, y)
    ax.set_title("Sample Scatter Plot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True)

    # Create KeyValueBox objects
    box1 = KeyValueBox(fig, edge_color='black', width=0.2, height=0.1, key="Classification:", value="Unclassified",
                       key_ha='left', key_va='top', value_ha='center', value_va='center')
    box2 = KeyValueBox(fig, edge_color='black', width=0.2, height=0.1, key="Status:", value="Active", key_ha='left',
                       key_va='top', value_ha='center', value_va='center')
    box3 = KeyValueBox(fig, edge_color='black', width=0.2, height=0.1, key="Level:", value="High", key_ha='left',
                       key_va='top', value_ha='center', value_va='center')
    box4 = KeyValueBox(fig, edge_color='black', width=box3.width * 3, height=box1.height, key="Status:",
                       value="Lorem ipsum dolor sit amet",
                       key_ha='left', key_va='top', value_ha='left', value_va='center')

    # Create ControlBlock and add KeyValueBoxes
    control_block = ControlBlock(fig, grid_rows=2, grid_cols=3, start_x=0, start_y=0)
    control_block.add_box(box1, row=0, col=0)
    control_block.add_box(box2, row=0, col=1)
    control_block.add_box(box3, row=0, col=2)
    control_block.add_box(box4, row=1, col=0)  # Spanning the entire row

    print(f"The control block size is: {control_block.get_size()}")
    print(f"The control block location is: {control_block.get_position()}")
    plot_position = ax.get_position()
    print(f"The plot location is: {plot_position.bounds}")
    print(f"The figure size is {fig.get_size_inches()}")

    while control_block.check_overlap():
        control_block.scale(0.9)

    # Adjust plot size and position based on control block position
    control_block_position = control_block.get_position()
    plot_position = ax.get_position().bounds

    # Define the gap size
    gap = 0.1

    # Check and adjust for vertical overlap with a gap
    if control_block_position[3] > plot_position[1]:  # Overlaps on the bottom
        overlap_height = control_block_position[3] - plot_position[1] + gap
        ax.set_position([plot_position[0], plot_position[1] + overlap_height,
                         plot_position[2], plot_position[3] - overlap_height])

    # Realign plot horizontally if it was shifted
    if control_block_position[2] > plot_position[0]:  # If it was shifted due to width
        original_width = plot_position[2] + plot_position[0]
        ax.set_position(
            [plot_position[0], ax.get_position().y0, original_width - ax.get_position().x0, ax.get_position().height])

    # Draw the control block
    control_block.draw()

    # Show the plot
    plt.show()
