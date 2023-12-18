from simlab.dataviz.scatter_plot import ScatterPlot
from simlab.dataviz import ureg


def main():
    x = [1, 2, 3, 4, 5] * ureg.hours
    y = [10, 20, 30, 40, 50] * ureg.miles

    scatter_plot = ScatterPlot(x, y, title='Sample Scatter Plot with Units',
                               quadgraph='ABCD', level='MILD')
    scatter_plot.create_plot()  # This creates the plot
    scatter_plot.save('scatter_plot_with_classification.png', dpi=300)  # Now save it


if __name__ == "__main__":
    main()

