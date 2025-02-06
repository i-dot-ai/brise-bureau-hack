from pydantic import BaseModel, Field
from typing import Union, List

class ProcessNode(BaseModel):
    unique_name: str
    description: str

class ProcessEdge(BaseModel):
    source: str
    target: str
    description: str

class ProcessMap(BaseModel):
    nodes: list[ProcessNode]
    edges: list[ProcessEdge]

    def get_node_set(self)-> set[str]:
        return set(node.unique_name for node in self.nodes)

    def get_edge_set(self)-> set[tuple[str, str]]:
        return set((edge.source, edge.target) for edge in self.edges)

    def add_node(self, node: ProcessNode) -> tuple[bool, str]:
        """
        Adds a node to the process map if it doesn't already exist.

        Args:
            node: The ProcessNode to add

                    Returns:
            tuple[bool, str]: A tuple containing:
                - bool: True if the node was added, False if it already existed
                - str: A message describing the result
        """
        if node.unique_name in self.get_node_set():
            return False, f"Node with name '{node.unique_name}' already exists"

        self.nodes.append(node)
        return True, f"Successfully added node '{node.unique_name}'"

class OutputApprovalModel(BaseModel):
    """
    Response from a resolver function that checks if a connection is valid. If not valid the message will contain the reason.
    """
    is_valid: bool
    message: str

class chatBotMessage(BaseModel):
    content: str = Field(..., description="The text content of a message to be sent to the user") 

class addNodeDecision(BaseModel):
    node: ProcessNode

class addEdgeDecision(BaseModel):
    edge: ProcessEdge

class chatBotDecision(BaseModel):
    message: chatBotMessage
    actions: List[Union[addNodeDecision, addEdgeDecision]]
