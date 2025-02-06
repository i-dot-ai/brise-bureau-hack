# CSS Templates need double curly braces to escape the curly braces in the f-string

TOPIC_CSS_TEMPLATE = """
<style>
    .member-card-{member_id} {{
        font-family: Arial, sans-serif;
        # border-radius: 8px;
        # padding: 16px;
        # margin-bottom: 16px;
        # max-width: 600px;
        # background-color: white;
        # box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    .member-header-{member_id} {{
        display: flex;
        align-items: center;
        margin-bottom: 16px;
    }}
    .member-thumbnail-{member_id} {{
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 16px;
        border: 3px solid {party_color};
    }}
    .member-name-{member_id} a {{
        color: #1a0dab;
        text-decoration: none;
    }}
    .member-name-{member_id} a:hover {{
        text-decoration: underline;
    }}
    .member-info-{member_id} {{
        flex-grow: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .party-tag-{member_id} {{
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        background-color: {party_color};
    }}
    .house-tag-{member_id} {{
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        background-color: {house_color};
    }}
    .stats-container-{member_id} {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
    }}
    .stat-box-{member_id} {{
        background-color: #f0f0f0;
        padding: 8px;
        border-radius: 4px;
        font-size: 14px;
        text-align: left;
        flex: 1;
        margin: 0 4px;
        position: relative;
    }}
    .stat-fill-{member_id} {{
        position: absolute;
        bottom: 0;
        left: 0;
        height: 4px;
        background-color: #4CAF50;
        transition: width 0.5s ease-in-out;
    }}
    .stat-label-{member_id} {{
        position: relative;
        z-index: 1;
    }}
    .headline-{member_id} {{
        font-style: italic;
        color: #555;
        margin-bottom: 12px;
    }}
    .show-more-{member_id} {{
        background-color: #f0f0f0;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
    }}
    .show-more-{member_id}::after {{
        content: "▼";
        font-size: 12px;
    }}
</style>
"""

TOPIC_HTML_TEMPLATE = """
<div class="member-card-{member_id}">
    <div class="member-header-{member_id}">
        <img src="https://i.pravatar.cc/100?u={member_id}" alt="Member Thumbnail" class="member-thumbnail-{member_id}">
        <div class="member-info-{member_id}">
            <div class="member-name-{member_id}">
                <a href="{member_url}">{member_name}</a>
            </div>
            <div class="tags-container-{member_id}">
                <span class="party-tag-{member_id}">{member_party_name}</span>
                <span class="house-tag-{member_id}">{house}</span>
            </div>
        </div>
    </div>
    <div class="stats-container-{member_id}">
        <div class="stat-box-{member_id}">
            <div class="stat-label-{member_id}">Sentiment: {sentiment}</div>
            <div class="stat-fill-{member_id}" style="width: {sentiment_fill}%;"></div>
        </div>
        <div class="stat-box-{member_id}">
            <div class="stat-label-{member_id}">Contributions: {n_contributions}</div>
            <div class="stat-fill-{member_id}" style="width: {contributions_fill}%;"></div>
        </div>
    </div>
    <div class="headline-{member_id}">{headline}</div>
</div>
"""

MP_CSS_TEMPLATE = """
<style>
.member-card-container {{
    width: 100%;
    max-width: 1200px;
    font-family: Arial, sans-serif;
    border: 2px solid {color};
    border-radius: 12px;
    padding: 20px;
}}

.member-container-{id} {{
    display: flex;
    width: 100%;
    align-items: center;
}}

.member-image-container-{id} {{
    flex-shrink: 0;
    margin-right: 20px;
}}

.member-image-{id} {{
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid {color};
}}

.member-content-{id} {{
    flex-grow: 1;
}}

.member-name-{id} {{
    font-size: 1.8rem;
    font-weight: bold;
    margin: 0 0 12px 0;
    color: #000;
}}

.member-synopsis-{id} {{
    font-size: 1rem;
    line-height: 1.5;
    margin: 0;
    color: #000;
}}

.member-link-{id} {{
    text-decoration: underline;
    color: #1a0dab;
}}
</style>
"""

MP_HTML_TEMPLATE = """
<div class="member-card-container">
    <div class="member-container-{id}">
        <div class="member-image-container-{id}">
            <img 
                src="{image_url}" 
                alt="{name}"
                class="member-image-{id}"
            >
        </div>
        <div class="member-content-{id}">
            <h1 class="member-name-{id}">{name}</h1>
            <p class="member-synopsis-{id}">
                {synopsis}
            </p>
        </div>
    </div>
</div>
"""

PARLEX_HTML_TEMPLATE = """
<div class="reference-item">
    <div class="reference-title">
        <a href="{link}" target="_blank" rel="noopener noreferrer">
            {title_html}
        </a>
    </div>
    <div class="reference-text markdown">
        {reference_html}
    </div>
</div>
"""

PARLEX_CSS = """
    <style>
      .parlex-container {
        font-family: system-ui, -apple-system, sans-serif;
        line-height: 1.5;
      }

      .response-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }

      .references-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
      }

      .reference-item {
        border-left: 3px solid #3b82f6;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #ffffff;
      }

      .reference-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
      }

      .reference-title a {
        color: #1e40af;
        text-decoration: none;
      }

      .reference-title a:hover {
        text-decoration: underline;
      }

      .reference-text {
        color: #374151;
        line-height: 1.6;
      }

      /* Markdown styles */
      .markdown p {
        margin: 0 0 1em 0;
      }
      
      .markdown p:last-child {
        margin-bottom: 0;
      }
      
      .markdown code {
        background-color: #f3f4f6;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: monospace;
      }
      
      .markdown pre {
        background-color: #f3f4f6;
        padding: 1em;
        border-radius: 6px;
        overflow-x: auto;
      }
      
      .markdown ul, .markdown ol {
        margin: 0 0 1em 0;
        padding-left: 2em;
      }
      
      .markdown h1, .markdown h2, .markdown h3, .markdown h4 {
        margin: 1em 0 0.5em 0;
      }
      
      .markdown h1:first-child, .markdown h2:first-child, 
      .markdown h3:first-child, .markdown h4:first-child {
        margin-top: 0;
      }
    </style>
    """
