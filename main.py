import numpy as np

from simlab.dataviz import ureg
from simlab.dataviz.scatter_plot import ScatterPlot


def main():
    # Initialize the ScatterPlot instance
    scatter_plot = ScatterPlot(
        title="Sample Scatter Plot with Units",
        quadgraph="ABCD",
        level="MILD",
        figsize=(10, 6),
    )

    # Generate and add 8 data series
    for i in range(8):
        x = np.linspace(1, 10, 10) * ureg.hours
        y = (i + 1) * np.linspace(1, 10, 10) * ureg.miles
        scatter_plot.add_data_series(x, y)

    # Create the plot
    scatter_plot.create_plot()

    # Specify the logo position
    scatter_plot.add_logo(logo_position="upper left")

    # Save the plot
    scatter_plot.save("scatter_plot_with_classification.png", dpi=300)


if __name__ == "__main__":
    main()
