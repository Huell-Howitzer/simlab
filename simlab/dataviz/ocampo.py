import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import PillowWriter
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

np.random.seed(19680801)

fig = plt.figure(figsize=(9, 8), facecolor="black")
ax = plt.subplot(frameon=False)

norm = Normalize(vmin=2.4, vmax=5)
cmap = plt.cm.viridis

# Increase the number of waveforms
num_waveforms = 30
data = np.random.uniform(0, 1, (num_waveforms, 50))
X = np.linspace(-1, 1, data.shape[-1])
G = 1.5 * np.exp(-4 * X**2)

lines = []
for i in range(len(data)):
    lw = 1.5 - i / 100.0
    (line,) = ax.plot(
        X, i + G * data[i], color=cmap(norm(2.4 + (5 - 2.4) * i / len(data))), lw=lw
    )
    lines.append(line)

ax.set_ylim(-1, num_waveforms)
ax.set_xticks([])
ax.set_yticks([])

ax.text(
    0.5,
    1.0,
    "MATPLOTLIB ",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    color="w",
    family="sans-serif",
    fontweight="light",
    fontsize=16,
)
ax.text(
    0.5,
    1.0,
    "UNCHAINED",
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    color="w",
    family="sans-serif",
    fontweight="bold",
    fontsize=16,
)


def update(*args):
    data[:, 1:] = data[:, :-1]
    data[:, 0] = np.random.uniform(0, 1, len(data))
    for i in range(len(data)):
        lines[i].set_ydata(i + G * data[i])
    return lines


anim = animation.FuncAnimation(fig, update, interval=50, blit=True, save_count=100)

sm = ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation="vertical", label="Frequency (GHz)")

# Set ticks and labels on the colorbar
cbar.set_ticks([2.4, 3.4, 4.4, 5])
cbar.set_ticklabels(["2.4 GHz", "3.4 GHz", "4.4 GHz", "5 GHz"])

anim.save("waveform_animation.gif", writer=PillowWriter(fps=20))
