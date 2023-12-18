import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import image as mpimg

from ..classification import add_classification_banner


class PlotBase(ABC):
    def __init__(self, title, classification, figsize, logo=None):
        self.title = title
        self.classification = classification
        self.figsize = figsize
        self.fig, self.ax = plt.subplots(figsize=self.figsize, constrained_layout=True)
        self.logo = logo

        if self.classification:
            add_classification_banner(self.fig, self.classification)

        # Initialize x_data and y_data as None
        self.x_data = None
        self.y_data = None

    def set_data(self, x_data, y_data):
        self.x_data = x_data
        self.y_data = y_data

    def create_plot(self):
        if self.x_data is not None and self.y_data is not None:
            self.ax.scatter(self.x_data, self.y_data, zorder=1)
        else:
            raise ValueError("Data not set")

    from matplotlib.offsetbox import OffsetImage, AnnotationBbox

    def add_logo(self, logo_path="/home/ryan-howell/projects/simlab/logo.png", logo_position="upper left", scale_factor=0.1):
        logo_image = mpimg.imread(logo_path)
        dpi = self.fig.dpi

        # Adjust scale of the image
        imagebox = OffsetImage(logo_image, zoom=scale_factor)

        # Define padding as a fraction of figure size
        padding_x = 0.025  # 2.5% of figure width
        # Adjust padding_y to position above the plot area
        padding_y_above = 0.1  # 10% above the figure height

        # Define position for the logo in figure space
        if logo_position == "upper left":
            position = (0 + padding_x, 1 + padding_y_above)
        elif logo_position == "upper right":
            position = (1 - padding_x, 1 + padding_y_above)
        # Other positions as needed...

        # Create an annotation box for the logo
        logo_box = AnnotationBbox(imagebox, position,
                                  xycoords='figure fraction',
                                  boxcoords="figure fraction",
                                  box_alignment=(0, 1),  # Align the top-left of the logo box with the position
                                  frameon=False)

        # Add the logo to the figure instead of the plot
        self.fig.add_artist(logo_box)

    def save(self, filename, **kwargs):
        bbox_extra_artists = kwargs.pop('bbox_extra_artists', None)
        plt.grid(True, which='both', color='white', linestyle='-', linewidth=0.9);
        plt.savefig(filename, bbox_inches='tight', bbox_extra_artists=bbox_extra_artists, **kwargs)

    def show(self):
        plt.show()

    @staticmethod
    @abstractmethod
    def _get_units_label(data):
        pass