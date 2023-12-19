import unittest

from simlab.dataviz.plot_base import PlotBase


# Test subclass of PlotBase for testing purposes
class TestPlot(PlotBase):
    def _get_units_label(self, data):
        return "Units"

    def create_plot(self):
        pass


class TestPlotBase(unittest.TestCase):
    def test_init(self):
        plot = TestPlot(title="Test Plot", classification="Test", figsize=(10, 6))
        self.assertIsNotNone(plot)

    def test_add_logo(self):
        plot = TestPlot(title="Test Plot", classification="Test", figsize=(10, 6))
        plot.add_logo(
            logo_path="/logo.png",
            logo_position="upper left",
        )
        # Asserts to check if logo was added correctly

    def test_save(self):
        plot = TestPlot(title="Test Plot", classification="Test", figsize=(10, 6))
        plot.create_plot()
        # Save to a temporary file and assert if the file exists


if __name__ == "__main__":
    unittest.main()
