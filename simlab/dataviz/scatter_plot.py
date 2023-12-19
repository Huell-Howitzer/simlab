from . import ureg
from .plot_base import PlotBase
from ..classification import QuadGraph, Level


class ScatterPlot(PlotBase):
    def __init__(
        self, title="Scatter Plot", quadgraph=None, level=None, figsize=(10, 6)
    ):
        # Use enums to set classification text
        classification_text = self._get_classification_text(quadgraph, level)
        super().__init__(title, classification_text, figsize)
        self.data_series = []  # Initialize an empty list for data series

    @staticmethod
    def _get_classification_text(quadgraph, level):
        # Construct classification text from enums
        if quadgraph and level:
            return f"{QuadGraph[quadgraph].value} - {Level[level].value}"
        elif quadgraph:
            return QuadGraph[quadgraph].value
        elif level:
            return Level[level].value
        else:
            return None

    def add_data_series(self, x_data, y_data):
        self.data_series.append((x_data, y_data))  # Add the data series to the list

    def create_plot(self):
        for x_data, y_data in self.data_series:
            # Check if data has 'magnitude' attribute (ureg.Quantity) or not (numpy array)
            x_values = x_data.magnitude if hasattr(x_data, "magnitude") else x_data
            y_values = y_data.magnitude if hasattr(y_data, "magnitude") else y_data
            self.ax.scatter(x_values, y_values)

        self.ax.set_title(self.title)

        if self.data_series:
            self.ax.set_xlabel(self._get_units_label(self.data_series[0][0]))
            self.ax.set_ylabel(self._get_units_label(self.data_series[0][1]))

    @staticmethod
    def _get_units_label(data):
        if isinstance(data, ureg.Quantity):
            return f"{data.units:~P}"
        return "Value"
