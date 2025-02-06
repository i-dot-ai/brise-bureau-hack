from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


def init():
    current_dir = Path(__file__).resolve().parent
    css_path = current_dir.parent / "static" / "styles" / "iai.css"
    js_path = current_dir.parent / "static" / "scripts" / "iai.js"

    with css_path.open() as file:
        css_content = file.read()

    with js_path.open() as file:
        js_content = file.read()

    st.markdown(
        f"""
        <style>{css_content}</style>
    """,
        unsafe_allow_html=True,
    )

    html_code = f"""
        <script>{js_content}</script>
    """
    components.html(html_code, height=0)
