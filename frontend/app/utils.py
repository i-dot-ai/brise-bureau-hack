import logging
import os
from shared_utils.schema import ProcessMap, ProcessNode, ProcessEdge
import streamlit as st

from frontend.app.backend_interface import BackendClient
from shared_utils.loading import get_elasticsearch_client, get_openai_client
from shared_utils.settings import Settings

logger = logging.getLogger(__name__)


def init_session_state():
    if "settings" not in st.session_state:
        st.session_state.settings = Settings()
    # headers
    if "headers" not in st.session_state:
        st.session_state.headers = {}
    # Elastic search client
    if "es_client" not in st.session_state:
        st.session_state.es_client = get_elasticsearch_client()
    # Auth token for hansard
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = st.session_state.headers.get("X-Amzn-Oidc-Data")
    if "backend_host" not in st.session_state:
        st.session_state.backend_host = os.getenv("BACKEND_HOST", "None")
    # Initialize backend client
    if "backend_client" not in st.session_state:
        st.session_state.backend_client = BackendClient()
    if "openai_client" not in st.session_state:
        st.session_state.openai_client = get_openai_client()
    if "process_map" not in st.session_state:
        dummy_nodes = [
            ProcessNode(unique_name="start", description="Initial process step"),
            ProcessNode(unique_name="review", description="Review documentation"),
            ProcessNode(unique_name="approve", description="Final approval step")
        ]
        dummy_edges = [
            ProcessEdge(source="start", target="review", description="Submit for review"),
            ProcessEdge(source="review", target="approve", description="Pass review")
        ]
        st.session_state.process_map = ProcessMap(nodes=dummy_nodes, edges=dummy_edges)
    # Initialize session state for conversation history
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "file_summary" not in st.session_state:
        st.session_state.file_summary = None
