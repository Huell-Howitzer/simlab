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
        # Enable constrained_layout
        self.fig, self.ax = plt.subplots(figsize=self.figsize, constrained_layout=True)
        self.logo = logo

        if self.classification:
            add_classification_banner(self.fig, self.classification)

    @abstractmethod
    def create_plot(self):
        pass

    from matplotlib.offsetbox import OffsetImage, AnnotationBbox

    def add_logo(self, logo_path="/home/ryan-howell/projects/simlab/logo.png", logo_position="upper right", scale_factor=0.1):
        logo_image = mpimg.imread(logo_path)
        dpi = self.fig.dpi

        # Adjust scale of the image
        imagebox = OffsetImage(logo_image, zoom=scale_factor)

        # Define position for the logo in figure space
        positions = {
            "upper right": (1, 1),
            "upper left": (0, 1),
            "lower right": (1, 0),
            "lower left": (0, 0),
            "center": (0.5, 0.5),
        }
        # Get the position for the logo
        position = positions.get(logo_position, (0.5, 0.5))

        # Create an annotation box for the logo
        logo_box = AnnotationBbox(imagebox, position,
                                  xycoords='figure fraction',
                                  boxcoords="figure fraction",
                                  box_alignment=(1 if 'right' in logo_position else 0,
                                                 1 if 'upper' in logo_position else 0),
                                  frameon=False)

        # Add the logo to the figure instead of the plot
        self.fig.add_artist(logo_box)

    def save(self, filename, **kwargs):
        bbox_extra_artists = kwargs.pop('bbox_extra_artists', None)
        plt.savefig(filename, bbox_inches='tight', bbox_extra_artists=bbox_extra_artists, **kwargs)

    def show(self):
        plt.show()

    @staticmethod
    @abstractmethod
    def _get_units_label(data):
        pass

