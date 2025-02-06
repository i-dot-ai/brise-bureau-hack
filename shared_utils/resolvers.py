from shared_utils.schema import OutputApprovalModel, ProcessEdge, ProcessMap

def is_valid_connection(processEdge: ProcessEdge, processMap: ProcessMap)-> OutputApprovalModel:
    processMapSet = processMap.get_node_set()
    if processEdge.source not in processMapSet or processEdge.target not in processMapSet:
        return OutputApprovalModel(is_valid=False, message="Source or target node not found in process map")
    else:
        return OutputApprovalModel(is_valid=True, message="")

# def is_valid_node(node: ProcessNode, processMap: ProcessMap)-> OutputApprovalModel:
#     return OutputApprovalModel(is_valid=True, message="")