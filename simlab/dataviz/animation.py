import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.widgets import Slider
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import pandas as pd
import pint


class WaveformAnimator:
    """

    """

    def __init__(self, num_lines=64, frequency_range=(2.4, 5)):
        self.ureg = pint.UnitRegistry()
        self.num_lines = num_lines
        self.frequency_range = frequency_range
        self.data = None
        self.fig, self.ax = None, None
        self.lines = []

    def set_data(self, data):
        self.data = data
        self.fig, self.ax = self.setup_plot()

    def setup_plot(self):
        fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
        plt.subplots_adjust(bottom=0.25)

        time_ax = fig.add_axes([0.1, 0.1, 0.8, 0.03], facecolor='lightgoldenrodyellow')
        self.slider = Slider(time_ax, 'Time', 0, len(self.data) - 1, valinit=0, valstep=1)

        ax.set_ylim(-1.5, 1.5)
        ax.set_xticks(np.arange(0, len(self.data)))
        ax.set_xticklabels(np.arange(0, len(self.data)))
        ax.set_xlabel('Time (seconds)')
        ax.set_yticks([])
        ax.grid(True)

        self.slider.on_changed(self.update_slider)

        return fig, ax

    def update_slider(self, val):
        frame = int(self.slider.val)
        self.update(frame, self.lines)

    def start_animation(self, file_type):
        norm = Normalize(vmin=self.frequency_range[0], vmax=self.frequency_range[1])
        cmap = plt.cm.jet
        self.lines = [self.ax.plot([], [], color=cmap(norm(self.frequency_range[0] +
                                                           (self.frequency_range[1] - self.frequency_range[
                                                               0]) * i / self.num_lines)), lw=1.5 - i / 100.0)[0]
                      for i in range(self.num_lines)]

        anim = animation.FuncAnimation(self.fig, self.update, frames=len(self.data), fargs=(self.lines,), interval=50,
                                       blit=True)
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        self.fig.colorbar(sm, ax=self.ax, orientation='vertical', label='Frequency (GHz)')
        plt.show()

    def update(self, frame, lines):
        if frame < len(self.data):
            for i, line in enumerate(lines):
                line.set_data(self.data.index, self.data.iloc[frame, :])
        return lines


if __name__ == "__main__":
    num_points = 100  # Number of data points (time steps)
    num_series = 64  # Number of separate data series (lines in the plot)

    data = np.random.randn(num_points, num_series)
    time_index = pd.date_range('2021-01-01', periods=num_points, freq='S')
    df = pd.DataFrame(data, index=time_index)

    animator = WaveformAnimator()
    animator.set_data(df)
    animator.start_animation('csv')