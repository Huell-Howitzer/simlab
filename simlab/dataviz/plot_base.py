from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
from matplotlib import image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

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

    @abstractmethod
    def create_plot(self):
        pass

    def add_logo(
        self,
        logo_path="/home/ryan-howell/projects/simlab/logo.png",
        logo_position="upper left",
        scale_factor=0.1,
    ):
        logo_image = mpimg.imread(logo_path)
        dpi = self.fig.dpi

        # Adjust scale of the image
        imagebox = OffsetImage(logo_image, zoom=scale_factor)

        # Define padding as a fraction of figure size
        padding_x = 0.025  # 2.5% of figure width
        padding_y_above = 0.1  # 10% above the figure height

        # Define position for the logo in figure space
        position = {
            "upper left": (0 + padding_x, 1 + padding_y_above),
            "upper right": (1 - padding_x, 1 + padding_y_above),
        }.get(
            logo_position, (0.5, 0.5)
        )  # Default to center

        # Create an annotation box for the logo
        logo_box = AnnotationBbox(
            imagebox,
            position,
            xycoords="figure fraction",
            boxcoords="figure fraction",
            box_alignment=(0.5, 0.5),
            frameon=False,
        )

        # Add the logo to the figure instead of the plot
        self.fig.add_artist(logo_box)

    def save(self, filename, **kwargs):
        bbox_extra_artists = kwargs.pop("bbox_extra_artists", None)
        plt.grid(True, which="both", color="white", linestyle="-", linewidth=0.9)
        plt.savefig(
            filename,
            bbox_inches="tight",
            bbox_extra_artists=bbox_extra_artists,
            **kwargs
        )

    def show(self):
        plt.show()

    @staticmethod
    @abstractmethod
    def _get_units_label(data):
        pass
