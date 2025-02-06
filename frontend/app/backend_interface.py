import sys
from typing import Any
from urllib.parse import urljoin

import requests
import streamlit as st

sys.path.append("..")

from shared_utils.settings import Settings

class BackendClient:
    def __init__(self):
        """
        Initializes the BackendClient with the backend host URL and headers.
        """
        if "settings" not in st.session_state:
            st.session_state.settings = Settings()
            
        if "headers" not in st.session_state:
            st.session_state.headers = {}
            
        self.header: str | None = st.session_state.headers.get("X-Amzn-Oidc-Data", None)
        self.backend_host: str = f"{st.session_state.settings.BACKEND_URL}/api/"

    def get(self, url: str, params: dict[str, Any] | None = None) -> requests.Response:
        """
        Sends a GET request to the specified URL with optional parameters.

        Args:
            url (str): The endpoint URL.
            params (Optional[Dict[str, Any]]): The query parameters for the request.

        Returns:
            requests.Response: The response from the GET request.
        """
        if self.header:
            return requests.get(
                urljoin(self.backend_host, url),
                params=params,
                headers={"X-Amzn-Oidc-Data": self.header},
                timeout=10,
            )
        else:
            return requests.get(urljoin(self.backend_host, url), params=params, timeout=10)


    def post(self, url, data=None):
        if self.header:
            return requests.post(
                urljoin(self.backend_host, url),
                data=data,
                headers={"X-Amzn-Oidc-Data": self.header},
            )
        else:
            return requests.post(url, data=data)

    def put(self, url, data=None):
        if self.header:
            return requests.put(
                urljoin(self.backend_host, url),
                data=data,
                headers={"X-Amzn-Oidc-Data": self.header},
            )
        else:
            return requests.put(url, data=data)

    def delete(self, url, data=None):
        if self.header:
            return requests.delete(
                urljoin(self.backend_host, url),
                headers={"X-Amzn-Oidc-Data": self.header},
            )
        else:
            return requests.delete(url, data=data)
