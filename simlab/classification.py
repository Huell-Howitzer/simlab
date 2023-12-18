# simlab/classification.py
from enum import Enum


class QuadGraph(Enum):
    ABCD = "Banner text for ABCD"
    EFGH = "Banner text for EFGH"
    # Add more as needed


class Level(Enum):
    MILD = "Banner text for Mild"
    MEDIUM = "Banner text for Medium"
    SPICY = "Banner text for Spicy"
    # Add more as needed


# Optional: Function to combine both classifications if needed
def get_combined_classification(quadgraph, level):
    return f"{QuadGraph[quadgraph].value} - {Level[level].value}"


def add_classification_banner(fig, classification_text, color='red', alpha=0.5):
    # This adds text to the top of the figure without creating a new Axes
    fig.text(0.5, 1.02, classification_text, ha='center', va='bottom', fontsize=14,
             fontweight='bold', color=color, bbox=dict(boxstyle="square,pad=0.2",
                                                       fc=color, alpha=alpha), transform=fig.transFigure)


