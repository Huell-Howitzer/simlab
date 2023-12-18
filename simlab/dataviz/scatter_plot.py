import matplotlib.pyplot as plt
import matplotlib.pyplot as plt


class ScatterPlot:
    def __init__(self, x_data, y_data, title='Scatter Plot', xlabel='X-axis', ylabel='Y-axis'):
        self.x_data = x_data
        self.y_data = y_data
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

    def create_plot(self):
        plt.scatter(self.x_data, self.y_data)
        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)

    def show(self):
        plt.show()

