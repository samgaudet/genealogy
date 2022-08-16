from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import networkx as nx

from pydantic import BaseModel
from pygsuite import Clients, Spreadsheet


SHEET_ID = "xxx"


Clients.local_file_auth(
    r"xxx"
)


class Ancestor(BaseModel):
    """Basic model to represent an ancestor and their information."""

    node_id: int
    name: str
    born: int
    parents: Optional[List[int]] = None
    relationships: Optional[List[int]] = None


def process_ancestor_row(row: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """Handle type conversions in row data.

    Args:
        row (Dict[str, Optional[str]]): An individual row of ancestry data.

    Returns a cleaned dictionary for a row.
    """
    row["node_id"] = int(row["node_id"])
    row["born"] = int(row["born"])
    row["parents"] = (
        [int(_id) for _id in row["parents"].split(",")]
        if row["parents"]
        else []
    )
    row["relationships"] = (
        [int(_id) for _id in row["relationships"].split(",")]
        if row["relationships"]
        else []
    )

    return row


def get_ancestors_from_sheet(
    sheet_id: str, sheet_name: str = "Sheet1"
) -> List[Ancestor]:
    """Read data from Google Sheet and return a list of Ancestor objects.

    Args:
        sheet_id (str): The sheet ID with ancestral data.
        sheet_name (str): The sheet name to look in.

    Returns a list of Ancestor objects.
    """
    sheet = Spreadsheet(id=sheet_id)
    records = sheet[sheet_name].dataframe.to_dict("records")

    return [Ancestor(**process_ancestor_row(row)) for row in records]


def define_nodes(graph: nx.Graph, ancestors: List[Ancestor]):
    """Iteratively define nodes for every ancestor.

    Args:
        graph (nx.Graph):
        ancestors (List[Ancestor]):
    """
    nodes = []
    for ancestor in ancestors:
        data = ancestor.dict()
        node_id = data.pop("node_id")
        nodes.append((node_id, data))

    graph.add_nodes_from(nodes)


def define_edges(graph: nx.Graph, ancestors: List[Ancestor]):
    """Iteratively define edges for every ancestor.

    Args:
        graph (nx.Graph):
        ancestors (List[Ancestor]):
    """
    edges = []
    for ancestor in ancestors:
        parents = ancestor.parents
        for parent in parents:
            edges.append((ancestor.node_id, parent))

    graph.add_edges_from(edges)


ancestors = get_ancestors_from_sheet(SHEET_ID)
for ancestor in ancestors:
    print(ancestor)

G = nx.Graph()

define_nodes(G, ancestors)
define_edges(G, ancestors)

labels = nx.get_node_attributes(G, "name")

nx.draw(G, labels=labels, with_labels=True, font_weight="bold")
plt.show()
