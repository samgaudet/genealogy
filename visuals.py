from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import networkx as nx

from pydantic import BaseModel
from pygsuite import Clients, Spreadsheet


SHEET_ID = "1WZJWZ8PwOesDfsB2ltd2AUNLsUHXQGGEVr2ETozEcPE"


with open(
    r"C:\Users\sgaud\git\genealogy\sheets_sa_credentials.json", "r"
) as cred_file:
    print(cred_file.read())
    import json
    test = json.loads(cred_file.read())
    print(type(test))
    from pprint import pprint
    pprint(test)
    Clients.authorize_string(cred_file.read())
# Clients.local_file_auth(
#     r"C:\Users\sgaud\git\genealogy\sheets_sa_credentials.json"
# )


class Ancestor(BaseModel):
    """Basic model to represent an ancestor and their information."""
    node_id: int
    full_name: str
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


def define_parental_edges(graph: nx.Graph, ancestors: List[Ancestor]):
    """Iteratively define edges for every ancestor.

    Args:
        graph (nx.Graph):
        ancestors (List[Ancestor]):
    """
    edges = []
    for ancestor in ancestors:
        parents = ancestor.parents
        for parent in parents:
            edges.append((parent, ancestor.node_id))

    graph.add_edges_from(edges, relationship="parent")


def define_relationship_edges(graph: nx.Graph, ancestors: List[Ancestor]):
    """Iteratively define the edges for every relationship.

    Args:
        graph (nx.Graph):
        ancestors (List[Ancestor]):
    """
    edges = []
    for ancestor in ancestors:
        relationships = ancestor.relationships
        for relationship in relationships:
            edges.append((relationship, ancestor.node_id))

    graph.add_edges_from(edges, relationship="partner")


ancestors = get_ancestors_from_sheet(SHEET_ID)
for ancestor in ancestors:
    print(ancestor)

G = nx.DiGraph()

define_nodes(G, ancestors)
define_parental_edges(G, ancestors)
# define_relationship_edges(G, ancestors)

print(G.nodes)

pos = nx.drawing.nx_pydot.graphviz_layout(G, prog="dot")  # twopi for fun
labels = nx.get_node_attributes(G, "full_name")

nx.draw(G, pos, labels=labels, with_labels=True, font_weight="bold")
plt.show()
