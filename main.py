from simlab.dataviz.scatter_plot import ScatterPlot
from simlab.dataviz import ureg  # Import ureg from your dataviz package


def main():
    # Sample data with units
    x = [1, 2, 3, 4, 5] * ureg.second
    y = [10, 20, 30, 40, 50] * ureg.meters

    # Create a scatter plot instance
    scatter_plot = ScatterPlot(x, y, title='Sample Scatter Plot with Units')

    # Create and show the plot
    scatter_plot.create_plot()
    scatter_plot.show()


if __name__ == "__main__":
    main()







