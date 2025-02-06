from typing import Union

from .schema import (
    ProcessMap,
    chatBotDecision,
    addNodeDecision,
    addEdgeDecision,
    chatBotMessage,
    ProcessNode,
    ProcessEdge,
    OutputApprovalModel
)

def handle_add_node(process_map: ProcessMap, action: addNodeDecision) -> OutputApprovalModel:
    """
    Handle adding a new node to the process map.
    
    Args:
        process_map: The current process map state
        action: The node addition action to process
        
    Returns:
        OutputApprovalModel indicating success/failure and a message
    """
    success, message = process_map.add_node(action.node)
    return OutputApprovalModel(is_valid=success, message=message)

def handle_add_edge(process_map: ProcessMap, action: addEdgeDecision) -> OutputApprovalModel:
    """
    Handle adding a new edge to the process map.
    
    Args:
        process_map: The current process map state
        action: The edge addition action to process
        
    Returns:
        OutputApprovalModel indicating success/failure and a message
    """
    # First verify both nodes exist
    node_set = process_map.get_node_set()
    if action.edge.source not in node_set:
        return OutputApprovalModel(
            is_valid=False,
            message=f"Source node '{action.edge.source}' does not exist"
        )
    
    if action.edge.target not in node_set:
        return OutputApprovalModel(
            is_valid=False,
            message=f"Target node '{action.edge.target}' does not exist"
        )
    
    # Check if edge already exists
    edge_set = process_map.get_edge_set()
    if (action.edge.source, action.edge.target) in edge_set:
        return OutputApprovalModel(
            is_valid=False,
            message=f"Edge from '{action.edge.source}' to '{action.edge.target}' already exists"
        )
    
    # Add the edge
    process_map.edges.append(action.edge)
    return OutputApprovalModel(
        is_valid=True,
        message=f"Successfully added edge from '{action.edge.source}' to '{action.edge.target}'"
    )

def process_chatbot_decision(
    process_map: ProcessMap,
    decision: chatBotDecision
) -> tuple[list[str], bool]:
    """
    Process a chatbot decision by handling each action and collecting messages.
    Structural changes (nodes and edges) are processed before messages.
    
    Args:
        process_map: The current process map state
        decision: The chatbot decision containing actions to process
        
    Returns:
        tuple containing:
            - list[str]: List of messages to send to the user
            - bool: Whether all actions were successful
    """
    messages = []
    all_successful = True
    
    # First handle structural changes (nodes and edges)
    for action in decision.actions:
        if isinstance(action, addNodeDecision):
            result = handle_add_node(process_map, action)
            messages.append(result.message)
            all_successful = all_successful and result.is_valid
        elif isinstance(action, addEdgeDecision):
            result = handle_add_edge(process_map, action)
            messages.append(result.message)
            all_successful = all_successful and result.is_valid
    
    # Then handle messages
    for action in decision.actions:
        if isinstance(action, chatBotMessage):
            messages.append(action.content)
            
    return messages, all_successful

def format_process_map_for_prompt(process_map: ProcessMap) -> str:
    """
    Converts the current state of the process map into a formatted string representation
    suitable for inclusion in the chatbot's prompt.
    
    Args:
        process_map: The current process map state
        
    Returns:
        A formatted string describing the current state of the process map
    """
    if not process_map.nodes and not process_map.edges:
        return "The process map is currently empty."
    
    # Format nodes section
    nodes_text = "Process Nodes:\n"
    for node in sorted(process_map.nodes, key=lambda x: x.unique_name):
        nodes_text += f"- {node.unique_name}: {node.description}\n"
    
    # Format edges section
    edges_text = "\nProcess Connections:\n"
    if process_map.edges:
        for edge in sorted(process_map.edges, key=lambda x: (x.source, x.target)):
            edges_text += f"- {edge.source} → {edge.target}: {edge.description}\n"
    else:
        edges_text += "- No connections defined yet\n"
    
    # Combine sections
    return f"{nodes_text}{edges_text}"

