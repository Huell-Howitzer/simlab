import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from ..classification import add_classification_banner


class PlotBase(ABC):
    def __init__(self, title, classification, figsize):
        self.title = title
        self.classification = classification
        self.figsize = figsize
        # Enable constrained_layout
        self.fig, self.ax = plt.subplots(figsize=self.figsize, constrained_layout=True)

        if self.classification:
            add_classification_banner(self.fig, self.classification)

    @abstractmethod
    def create_plot(self):
        pass

    def save(self, filename, **kwargs):
        bbox_extra_artists = kwargs.pop('bbox_extra_artists', None)
        plt.savefig(filename, bbox_inches='tight', bbox_extra_artists=bbox_extra_artists, **kwargs)

    def show(self):
        plt.show()

    @staticmethod
    @abstractmethod
    def _get_units_label(data):
        pass

