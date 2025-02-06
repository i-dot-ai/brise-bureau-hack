from .schema import ProcessMap

def process_map_to_mermaid(process_map: ProcessMap) -> str:
    """
    Convert a ProcessMap object into a Mermaid diagram string.
    
    Args:
        process_map: ProcessMap object containing nodes and edges
        
    Returns:
        str: Mermaid diagram representation as a string
    """
    # Start the flowchart definition
    mermaid_lines = ["flowchart TD"]
    
    # Add nodes
    for node in process_map.nodes:
        # Create node with ID and description in a box
        # Escape quotes in description to prevent syntax errors
        safe_description = node.description.replace('"', '\\"')
        node_line = f'    {node.unique_name}["{safe_description}"]'
        mermaid_lines.append(node_line)
    
    # Add edges
    for edge in process_map.edges:
        # Escape quotes in description to prevent syntax errors
        safe_description = edge.description.replace('"', '\\"')
        # Create edge with description
        edge_line = f'    {edge.source} -->|"{safe_description}"| {edge.target}'
        mermaid_lines.append(edge_line)
    
    # Join all lines with newlines
    return "\n".join(mermaid_lines)
