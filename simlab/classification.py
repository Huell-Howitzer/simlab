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
