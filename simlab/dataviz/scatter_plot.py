from .plot_base import PlotBase
from . import ureg
from ..classification import QuadGraph, Level, add_classification_banner


class ScatterPlot(PlotBase):
    def __init__(self, x_data, y_data, title='Scatter Plot', quadgraph=None, level=None, figsize=(10, 6)):
        # Use enums to set classification text
        classification_text = self._get_classification_text(quadgraph, level)
        super().__init__(title, classification_text, figsize)
        self.x_data = x_data
        self.y_data = y_data
        self.xlabel = self._get_units_label(x_data)
        self.ylabel = self._get_units_label(y_data)

    @staticmethod
    def _get_classification_text(quadgraph, level):
        # Construct classification text from enums, if provided
        if quadgraph and level:
            return f"{QuadGraph[quadgraph].value} - {Level[level].value}"
        elif quadgraph:
            return QuadGraph[quadgraph].value
        elif level:
            return Level[level].value
        else:
            return None

    @staticmethod
    def _get_units_label(data):
        if isinstance(data, ureg.Quantity):
            return f"{data.units:~P}"
        return "Value"

    def create_plot(self):
        self.ax.scatter(self.x_data.magnitude, self.y_data.magnitude)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
