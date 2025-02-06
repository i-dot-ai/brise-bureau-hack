import streamlit.components.v1 as components

def render_mermaid(mermaid_flowchart):
    components.html(
        f"""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.min.js"></script>
        <div class="mermaid-container" style="overflow-y: auto; max-height: 750px;">
            <div class="mermaid">
            {mermaid_flowchart}
            </div>
        </div>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                fontFamily: 'monospace, sans-serif',
                flowchart: {{
                    htmlLabels: true,
                    useMaxWidth: true,
                }},
                securityLevel: 'loose',
            }});
            mermaid.parseError = function(err, hash) {{
                console.error('Mermaid error:', err);
            }};
        </script>
        """,
        height=750,
    )