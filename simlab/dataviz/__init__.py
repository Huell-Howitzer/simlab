from pathlib import Path
import pint
import matplotlib.pyplot as plt

ureg = pint.UnitRegistry()
ureg.setup_matplotlib(True)

style_file = Path(__file__).parent.absolute() / 'style' / 'matplotlibrc'
plt.style.use(str(style_file))