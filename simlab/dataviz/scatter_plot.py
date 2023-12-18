import matplotlib.pyplot as plt
from . import ureg  # Assuming this is the correct relative import path in your package


class ScatterPlot:
    def __init__(self, x_data, y_data, title='Scatter Plot'):
        self.x_data = x_data
        self.y_data = y_data
        self.title = title
        self.xlabel = self._get_units_label(x_data)
        self.ylabel = self._get_units_label(y_data)

    def _get_units_label(self, data):
        if isinstance(data, ureg.Quantity):
            return f"{data.units:~P}"  # Pretty print with units
        return "Value"  # Default label if no units

    def create_plot(self):
        plt.scatter(self.x_data.magnitude, self.y_data.magnitude)
        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)

    def show(self):
        plt.show()






