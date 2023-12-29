import matplotlib.pyplot as plt
import numpy as np
import svgwrite
import cairosvg
import matplotlib.image as mpimg
from PIL import Image
from io import BytesIO
import matplotlib.backends.backend_agg as agg

class BaseFigureWithCustomSVGGrid:
    def __init__(self, text_data, figsize=(12, 8), cell_size=50, margin=10, padding=5, text_style=None):
        """
        Initialize the BaseFigure with a custom SVG grid.

        :param text_data: Dictionary mapping grid positions to (key_text, value_text).
        :param figsize: Tuple for figure size (width, height).
        :param cell_size: Base size of each cell in the grid.
        :param margin: Margin around the grid.
        :param padding: Padding between cells.
        :param text_style: Dictionary with text style options like color and bold.
        """
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.text_data = text_data
        self.cell_size = cell_size
        self.margin = margin
        self.padding = padding
        self.text_style = text_style if text_style else {}
        self.create_custom_svg_grid()

    def create_custom_svg_grid(self):
        """ Create a custom SVG grid based on the specified text data. """
        # Grid layout: 1 row spanning full width, 3 cells in second row, 2 cells in third row
        grid_layout = [(1,), (3,), (2,)]
        
        total_width = sum(grid_layout[0]) * self.cell_size + (sum(grid_layout[0]) - 1) * self.padding
        total_height = len(grid_layout) * self.cell_size + (len(grid_layout) - 1) * self.padding

        # Create SVG drawing
        svg = svgwrite.Drawing(size=(total_width, total_height))
        current_y = self.margin

        # Create grid cells and add text
        for row in grid_layout:
            current_x = self.margin
            for col_span in row:
                col_width = col_span * self.cell_size + (col_span - 1) * self.padding
                self.add_cell(svg, current_x, current_y, col_width, self.cell_size, self.text_data.get((len(grid_layout), col_span), ("", "")))
                current_x += col_width + self.padding
            current_y += self.cell_size + self.padding

        # Embed the SVG in the figure
        self.embed_svg(svg.tostring())

    def add_cell(self, svg, x, y, width, height, cell_text):
        """ Add a cell with text to the SVG. """
        key_text, value_text = cell_text
        svg.add(svg.rect(insert=(x, y), size=(width, height), fill='none', stroke='black'))
        # Add text with styling
        svg.add(svg.text(key_text, insert=(x + self.padding, y + 20), fill=self.text_style.get('color', 'black'), font_weight='bold' if self.text_style.get('bold') else 'normal'))
        svg.add(svg.text(value_text, insert=(x + self.padding, y + height - 10), fill=self.text_style.get('color', 'black')))

    def embed_svg(self, svg_string):
        """ Embed the SVG string in the Matplotlib figure. """
        png_output = cairosvg.svg2png(bytestring=svg_string)
        img = mpimg.imread(BytesIO(png_output), format='PNG')
        # Position the grid below the scatter plot
        self.fig.figimage(img, xo=0, yo=self.fig.bbox.ymax - img.shape[0] - self.cell_size)

    def add_scatter_plot(self, x, y, title="Scatter Plot"):
        """ Add a scatter plot to the figure. """
        self.ax.scatter(x, y)
        self.ax.set_title(title)

    def save_figure(self, filename):
        """ Save the figure to a file. """
        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        canvas.print_png(filename)

# Example usage
# Corrected example usage
text_data = {
    (1, 1): ("Title", "Top Row Spanning All Columns"),
    (2, 1): ("Box1", "Value1"), 
    (2, 2): ("Box2", "Value2"), 
    (2, 3): ("Box3", "Value3"),
    (3, 1): ("Half1", "Value4"), 
    (3, 2): ("Half2", "Value5")
}
text_style = {"color": "blue", "bold": True}
fig_with_custom_svg_grid = BaseFigureWithCustomSVGGrid(text_data, text_style=text_style)
x = np.random.rand(50)
y = np.random.rand(50)
fig_with_custom_svg_grid.add_scatter_plot(x, y, "Scatter Plot with Custom SVG Grid")
fig_with_custom_svg_grid.save_figure('figure_with_custom_svg_grid.png')