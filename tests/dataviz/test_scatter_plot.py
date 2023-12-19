import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

from simlab.dataviz import ureg
from simlab.dataviz.scatter_plot import ScatterPlot


class TestScatterPlot(unittest.TestCase):
    def setUp(self):
        # Any setup you want to do before each test goes here
        self.test_output_path = Path("test_output.png")
        self.reference_image_path = Path("../resources/scatter_test000.png")

    def test_init(self):
        plot = ScatterPlot(title="Test Scatter Plot", quadgraph="ABCD", level="MILD")
        self.assertIsNotNone(plot)

    def test_create_plot(self):
        plot = ScatterPlot(title="Test Scatter Plot", quadgraph="ABCD", level="MILD")
        x_data = np.array([1, 2, 3, 4, 5])
        y_data = np.array([10, 20, 30, 40, 50])
        plot.add_data_series(x_data, y_data)
        plot.create_plot()

    def test_add_data_series(self):
        plot = ScatterPlot(title="Test Scatter Plot", quadgraph="ABCD", level="MILD")
        x_data = np.array([1, 2, 3, 4, 5])
        y_data = np.array([10, 20, 30, 40, 50])
        plot.add_data_series(x_data, y_data)
        self.assertEqual(len(plot.data_series), 1)

    def test_plot_visuals(self):
        # Generate a new plot
        scatter_plot = ScatterPlot(
            title="Sample Scatter Plot with Units",
            quadgraph="ABCD",
            level="MILD",
            figsize=(10, 6),
        )
        for i in range(8):
            x = np.linspace(1, 10, 10) * ureg.hours
            y = (i + 1) * np.linspace(1, 10, 10) * ureg.miles
            scatter_plot.add_data_series(x, y)
        scatter_plot.create_plot()
        scatter_plot.add_logo(logo_position="upper left")
        scatter_plot.save(self.test_output_path, dpi=300)

        # Compare the generated plot with the reference image
        with Image.open(self.reference_image_path) as baseline_img, Image.open(
            self.test_output_path
        ) as test_img:
            diff = ImageChops.difference(baseline_img, test_img)
            self.assertIsNone(
                diff.getbbox(), "Generated plot image differs from the baseline image."
            )

    def tearDown(self):
        # Delete the test output file after each test
        if self.test_output_path.exists():
            self.test_output_path.unlink()


if __name__ == "__main__":
    unittest.main()
