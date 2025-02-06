from shared_utils.schema import ProcessMap, ProcessNode, ProcessEdge
from shared_utils.mermaid import process_map_to_mermaid

from shared_utils.prompts import get_process_mapping_prompt  # Assuming this is the function we want to test

def create_test_process_map() -> ProcessMap:
    # Create nodes for a document approval workflow
    nodes = [
        ProcessNode(
            unique_name="draft_document",
            description="Initial creation of the document draft by the author"
        ),
        ProcessNode(
            unique_name="review_document",
            description="Document is reviewed by the designated reviewer"
        ),
        ProcessNode(
            unique_name="revise_document",
            description="Author makes requested revisions to the document"
        ),
        ProcessNode(
            unique_name="approve_document",
            description="Final approval of the document by authorized personnel"
        )
    ]

    # Create edges showing the workflow connections
    edges = [
        ProcessEdge(
            source="draft_document",
            target="review_document",
            description="Document submitted for initial review"
        ),
        ProcessEdge(
            source="review_document",
            target="revise_document",
            description="Changes requested by reviewer"
        ),
        ProcessEdge(
            source="revise_document",
            target="review_document",
            description="Revised document submitted for another review"
        ),
        ProcessEdge(
            source="review_document",
            target="approve_document",
            description="Document approved by reviewer"
        )
    ]

    return ProcessMap(nodes=nodes, edges=edges)

def test_prompt_construction_with_mocked_chat():
    # Mock chat history
    mock_chat = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I help?"},
        {"role": "user", "content": "I need help with Python"}
    ]
    
    # Create the prompt
    prompt = construct_prompt(mock_chat)
    
    # Print the example prompt for inspection
    print("\nExample constructed prompt:")
    print(prompt)
    
    # Basic assertions
    assert isinstance(prompt, str)
    assert "Hello" in prompt
    assert "Hi there! How can I help?" in prompt
    assert "I need help with Python" in prompt

# Example usage
if __name__ == "__main__":
    process_map = create_test_process_map()
    # You can print the node and edge sets to verify the structure
    print("Nodes:", process_map.get_node_set())
    print("Edges:", process_map.get_edge_set())
    print(process_map_to_mermaid(process_map))
    print(get_process_mapping_prompt(process_map_to_mermaid(process_map)))