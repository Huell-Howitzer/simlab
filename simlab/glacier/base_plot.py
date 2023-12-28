import matplotlib.patches as patches
import matplotlib.pyplot as plt


class Box:
    def __init__(self, fig, text, x, y, edge_color, width=0.15, height=0.03, text_ha='left'):
        self.fig = fig
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.edge_color = edge_color
        self.text_ha = text_ha

    def draw(self):
        # Create a rectangle patch for the border box
        rect = patches.Rectangle((self.x, self.y), self.width, self.height, transform=self.fig.transFigure,
                                 linewidth=2, edgecolor=self.edge_color, facecolor='none')
        self.fig.patches.append(rect)

        # Add text within the box
        text_x = self.x + 0.01 if self.text_ha == 'left' else self.x + self.width / 2
        self.fig.text(text_x, self.y + self.height / 2, self.text, transform=self.fig.transFigure,
                      ha=self.text_ha, va='center')


# Create a figure with a specific size
fig = plt.figure(figsize=(8, 7))
ax = fig.add_axes([0.1, 0.4, 0.8, 0.55])  # Adjust to create space at the bottom

# Create and draw boxes
your_text_box = Box(fig, 'Your Text Here', 0.06, 0.12, 'red')
your_text_box.draw()
created_by_box = Box(fig, 'Created By: ', 0.06, 0.15, 'blue')
created_by_box.draw()
logo_box = Box(fig, 'Logo', 0.0, 0.12, 'green', width=0.06, height=0.06, text_ha='center')
logo_box.draw()
classification_box = Box(fig, 'Classification', 0.0, 0.18, 'orange', width=0.45, height=0.06, text_ha='left')
classification_box.draw()
notes_box = Box(fig, 'Notes', 0.0, 0.0, 'yellow', width=0.45, height=0.12, text_ha='center')
notes_box.draw()
address_line1_box = Box(fig, '1 Administration Circle', 0.21, 0.15, 'purple', width=0.24, height=0.03, text_ha='left')
address_line1_box.draw()
city_box = Box(fig, 'China Lake', 0.21, 0.12, 'purple', width=0.12, height=0.03, text_ha='left')
city_box.draw()
state_box = Box(fig, 'CA', 0.33, 0.12, 'purple', width=0.04, height=0.03, text_ha='center')
state_box.draw()
zipcode_box = Box(fig, '93555', 0.37, 0.12, 'purple', width=0.08, height=0.03, text_ha='center')
zipcode_box.draw()

# Show the plot
plt.show()
