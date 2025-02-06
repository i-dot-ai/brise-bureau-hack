import calendar
import logging
import json
import re
from datetime import datetime
from typing import Generator

from contribution_card_templates import TOPIC_CSS_TEMPLATE, TOPIC_HTML_TEMPLATE
import plotly.express as px
import requests
import streamlit as st
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MEMBER_SUMMARY_TIMOUT = 10

PARLEX_BY_TOPIC_EXPLANATION_TEXT = """
*Parlex will provide you with a summary of the views and contributions of Members of Parliament on a topic of your choice. It will look for members with relevant contributions and then retrieve further background information about these members to ensure it has the most relevant information to hand.*
"""

BACKEND_URL = "http://localhost:8080"


class ContributionData:
    """
    A class to manage and filter contribution data related to bill summaries.

    Attributes:
        bill_summary (str): A summary of the bill.
        contributions (list): A list to store contributions.
        parties (set): A set to store unique party names.
        houses (set): A set to store unique house names.
        filters (dict): A dictionary to store filtering criteria.

    Methods:
        add_contribution(contribution):
            Adds a contribution to the contributions list and updates the filter criteria.

        set_sentiment_range(sentiment_range):
            Sets the sentiment range filter.

        set_party_filter(party_filter):
            Sets the party filter.

        set_house_filter(house_filter):
            Sets the house filter.

        filtered_data():
            Returns a list of contributions that match the current filters.

        summarise_contributions():
            Returns a summary of contributions with member names and their summaries.
    """

    def __init__(self, bill_summary):
        self.bill_summary = bill_summary
        self.contributions = []
        self.parties = set()
        self.houses = set()
        self.filters = {
            "sentiment_range": (1, 10),
            "party_filter": [],
            "house_filter": [],
        }

    def add_contribution(self, contribution):
        self.contributions.append(contribution)
        # TODO: add parties and house to the member index in ingestion
        self.parties.add(contribution["contributions"][0]["member_party_name"])
        self.houses.add(contribution["contributions"][0]["house"])
        self.filters["party_filter"] = list(self.parties)
        self.filters["house_filter"] = list(self.houses)

    def set_sentiment_range(self, sentiment_range):
        self.filters["sentiment_range"] = sentiment_range

    def set_party_filter(self, party_filter):
        self.filters["party_filter"] = party_filter

    def set_house_filter(self, house_filter):
        self.filters["house_filter"] = house_filter

    def filtered_data(self):
        return [
            contribution
            for contribution in self.contributions
            if (
                contribution["bill_sentiment"] >= self.filters["sentiment_range"][0]
                and contribution["bill_sentiment"] <= self.filters["sentiment_range"][1]
                and contribution["contributions"][0]["member_party_name"] in self.filters["party_filter"]
                and contribution["contributions"][0]["house"] in self.filters["house_filter"]
            )
        ]

    def summarise_contributions(self):
        return [
            {
                "member_name": member_contributions["contributions"][0]["member_name"],
                "summary": member_contributions["summary"],
            }
            for member_contributions in self.filtered_data()
        ]


class SentimentHistogram:
    """
    A class used to represent a histogram of sentiment scores by party.

    Attributes
    ----------
    data : dict
        A dictionary to store sentiment scores and corresponding party names.
    party_to_color : dict
        A dictionary to map party names to their respective colors.
    plot_container : object
        A container object to hold the plot.
    """

    def __init__(self, plot_container):
        self.data = {
            "sentiment": [],
            "member_party_name": [],
        }
        self.party_to_color = {}
        self.plot_container = plot_container

    def add_data(self, contributions):
        """
        Adds contribution data to the instance's data attributes.

        Args:
            contributions (dict): A dictionary containing contribution data.
            Expected keys are:
            - "contributions" (list): A list of dictionaries, each containing:
                - "member_party_name" (str): The name of the member's party.
                - "member_party_background_colour" (str): The background color associated with the member's party.
            - "bill_sentiment" (str): The sentiment associated with the bill.

        Modifies:
            self.data (dict): Updates the "sentiment" and "member_party_name" lists with the corresponding data from contributions.
            self.party_to_color (dict): Maps each member's party name to its background color.
        """
        for contribution in contributions["contributions"]:
            self.data["sentiment"].append(contributions["bill_sentiment"])
            self.data["member_party_name"].append(contribution["member_party_name"])
            self.party_to_color[contribution["member_party_name"]] = (
                f"#{contribution['member_party_background_colour']}"
            )

    def plot(self):
        """
        Plots a histogram of sentiment distribution by party.

        This method creates a stacked histogram using Plotly Express to visualize
        the distribution of sentiment scores across different political parties.
        The histogram is colored by party and displays the count of contributions
        for each sentiment score.

        The x-axis represents sentiment scores ranging from 1 to 10, and the y-axis
        represents the number of contributions. The plot includes a title and
        labels for both axes. The hover template shows the sentiment score and
        count for each bar.

        The plot is rendered in the plot container with the width adjusted to fit
        the container.

        Attributes:
            self.data (pd.DataFrame): DataFrame containing the sentiment scores and
                party names.
            self.party_to_color (dict): Dictionary mapping party names to colors.
            self.plot_container (st.delta_generator.DeltaGenerator): Streamlit plot
                container to render the plot.
        """
        fig = px.histogram(
            x=self.data["sentiment"],
            color=self.data["member_party_name"],
            # color_discrete_map=self.party_to_color,
            nbins=10,
            range_x=[1, 10],
            labels={"sentiment": "Sentiment", "member_party_name": "Party"},
            title="Distribution of sentiment by party",
        )
        fig.update_traces(hovertemplate="Sentiment: %{x}<br>Count: %{y}<extra></extra>")
        fig.update_layout(
            xaxis_title="Sentiment",
            yaxis_title="Number of Contributions",
            barmode="stack",
        )
        self.plot_container.plotly_chart(fig, use_container_width=True)


def clean_xml_tags(text: str) -> str:
    """
    Remove all XML/HTML tags from text while preserving the content between tags.

    Args:
        text (str): Input text containing XML/HTML tags

    Returns:
        str: Cleaned text with all tags removed
    """
    # This pattern matches any XML/HTML tag: <...>
    pattern = r"<[^>]+>"

    # Use re.sub to replace all matches with empty string
    cleaned_text = re.sub(pattern, "", text)

    return cleaned_text


def render_member_card(member: dict, n_contributions: int, sentiment_fill: float, contributions_fill: float) -> str:
    member_id = hash(member["member_id"])
    # member_id = member["member_id"]
    party_color = "#" + member["contributions"][0]["member_party_background_colour"]
    house_color = "#" + member["contributions"][0]["member_house_background_colour"]

    css_content = TOPIC_CSS_TEMPLATE.format(member_id=member_id, party_color=party_color, house_color=house_color)

    html_content = TOPIC_HTML_TEMPLATE.format(
        member_id=member_id,
        member_url=member["contributions"][0]["member_url"],
        member_name=member["contributions"][0]["member_name"],
        member_party_name=member["contributions"][0]["member_party_name"],
        house=member["contributions"][0]["house"],
        sentiment=member["bill_sentiment"],
        member_avg_score=member["member_avg_score"],
        n_contributions=n_contributions,
        headline=member["headline"],
        sentiment_fill=sentiment_fill * 100,
        contributions_fill=contributions_fill * 100,
    )

    full_html = f"""
    <div>
        {css_content}
        {html_content}
    </div>
    """

    return full_html


def display_contribution(member: dict) -> None:
    """
    Display the contributions of a member in a Streamlit container.

    Args:
        member (dict): A dictionary containing member information and their contributions.
        container (st.container): A Streamlit container to display the content.
        bill_summary (str): A summary of the bill related to the contributions.

    Returns:
        None
    """
    member_contributions = member["contributions"]

    with st.container():  # fixes a bug where subsequent contributions overwrite the buttons of previous ones
        st.html(
            render_member_card(
                member,
                len(member_contributions),
                member["bill_sentiment"] / 10,
                len(member_contributions) / st.session_state.max_contributions,
            )
        )

        with st.expander("Show contributions"):
            for contribution_id, contribution in enumerate(member_contributions, 1):
                st.markdown(
                    f"**[Contribution {contribution_id}]({contribution['contribution_url']})** (Relevance score: {contribution['score']:.2f})"
                )

                st.markdown(
                    f"Contribution was made on [{contribution['date']}]({contribution['chamber_date_url']}) in the {contribution['house']} chamber as part of the [{contribution['debate_title']}]({contribution['debate_url']}) debate."
                )

                highlighted_text = contribution["text"]
                for indicative_quote in member["indicative_quotes"]:
                    # highlight the indicative quote
                    highlighted_text = re.sub(
                        re.escape(indicative_quote),
                        f"**{indicative_quote}**",
                        highlighted_text,
                        flags=re.IGNORECASE,
                    )
                    highlighted_text = clean_xml_tags(highlighted_text)
                st.markdown(
                    highlighted_text,
                )
                st.divider()

        st.markdown("---")


@st.fragment
def filter_data():
    st.session_state.contributions.set_sentiment_range(st.session_state.sentiment_range_filter)
    st.session_state.contributions.set_party_filter(st.session_state.party_filter)

    with st.session_state.parlex_containers["contributions"]:
        with st.container():
            st.subheader("Member Contributions")
            sort_by = st.radio(
                "Sort contributions by sentiment",
                ["None", "Highest sentiment first", "Lowest sentiment first"],
                horizontal=True,
                key="sort_contributions",
            )

            if sort_by == "Highest sentiment first":
                st.session_state.contributions.filtered_data().sort(key=lambda x: x["bill_sentiment"], reverse=True)
            elif sort_by == "Lowest sentiment first":
                st.session_state.contributions.filtered_data().sort(key=lambda x: x["bill_sentiment"])
            with st.container(border=True):
                for contribution in st.session_state.contributions.filtered_data():
                    display_contribution(contribution)


@st.fragment
def create_filters():
    st.subheader("Filter contributions")
    # voting intention filter
    st.slider(
        "Opinion Sentiment range",
        min_value=1,
        max_value=10,
        value=(1, 10),
        step=1,
        key="sentiment_range_filter",
        on_change=filter_data,
    )

    # filter by party
    st.multiselect(
        "Party",
        options=st.session_state.contributions.parties,
        default=st.session_state.contributions.filters["party_filter"],
        key="party_filter",
        on_change=filter_data,
    )


@st.fragment
def display_subgroup_summary():
    st.subheader("Subgroup summary")

    if st.button("Generate subgroup summary"):
        with st.spinner("Generating subgroup summary..."):
            response = requests.post(
                f"{BACKEND_URL}/parlex/subgroup-summary",
                json={"summaries": st.session_state.contributions.summarise_contributions()},
            )
            response.raise_for_status()
            response = response.json()

            st.write(f"**Summary:** {response['headline']}")
            with st.expander("Show subgroup summary", expanded=True):
                st.write(response["summary"])

    else:
        return


def load_contributions(num_contributions: int, month_range: tuple[str, str]) -> Generator[dict, None, None]:
    """
    Load member contributions within a specified date range.

    Args:
        num_contributions (int): The number of contributions to load.
        month_range (tuple[str, str]): A tuple containing the start and end month in the format 'Month Year'.

    Yields:
        dict: A dictionary containing the contribution data.

    Raises:
        requests.exceptions.ChunkedEncodingError: If an error occurs while streaming the response.

    This function performs the following steps:
        1. Converts the month_range strings to datetime.date objects.
        2. Constructs search parameters for the backend request.
        3. Sends a request to the backend to search for contributions.
        4. Processes the streaming response, updating progress and displaying contributions.
        5. Handles errors that occur during the streaming response.
        6. Updates the UI with filters and subgroup summaries after processing contributions.
    """

    with st.spinner("Searching member contributions..."):
        # turn string like 'January 2020' to datetime.date(2023, 10, 1)
        first_date = datetime.strptime(month_range[0], "%B %Y").date()
        # get the last day of the month
        last_date = datetime.strptime(month_range[1], "%B %Y").date()
        last_date = last_date.replace(day=calendar.monthrange(last_date.year, last_date.month)[1])

        # TODO: move elasticsearch logging to backend

        search_params = {
            "user_query": st.session_state.bill_summary,
            "month_range": [first_date.isoformat(), last_date.isoformat()],
            "num_contributions": num_contributions,
        }

        # print(search_params)

        with requests.post(f"{BACKEND_URL}/parlex/topic-search", json=search_params, stream=True) as search_response:
            search_response.raise_for_status()
            try:
                for line in search_response.iter_lines():
                    result = json.loads(line)

                    if result["message_type"] == "summary":
                        with st.session_state.parlex_containers["progress"]:
                            progress_bar = st.progress(0, text="Analysing member positions...")
                        voting_intentions_plot = SentimentHistogram(st.session_state.parlex_containers["histogram"])

                        total_tasks = result["number_results"]
                        st.session_state.max_contributions = result["max_contributions"]
                        completed_counter = 0

                        with st.session_state.parlex_containers["contributions"]:
                            with st.container():
                                st.subheader("Member Contributions")
                                contribution_container = st.container(border=True)

                    elif result["message_type"] == "contribution":
                        completed_counter += 1
                        voting_intentions_plot.add_data(result["contribution"])
                        voting_intentions_plot.plot()
                        st.session_state.contributions.add_contribution(result["contribution"])

                        with contribution_container:
                            display_contribution(result["contribution"])

                        progress = completed_counter / total_tasks
                        progress_bar.progress(
                            progress,
                            text=f"Analysing member positions... {completed_counter}/{total_tasks} completed",
                        )
                    else:
                        yield ""

            except requests.exceptions.ChunkedEncodingError as e:
                logger.error(f"Error while streaming response: {e}")
                st.error("An error occurred while streaming the response. Please try rerunning the analysis.")

            progress_bar.empty()
            with st.session_state.parlex_containers["filters"]:
                create_filters()

            # with st.session_state.parlex_containers["subgroups"]:
            #     with st.container():
            #         display_subgroup_summary()


def research_by_topic():
    st.title("Parlex, research by topic :scales:")

    st.markdown(
        PARLEX_BY_TOPIC_EXPLANATION_TEXT.format(
            n_relevant_contributions=st.session_state.get("num_contributions", 150),
            n_recent_contributions=20,
            n_written_questions=20,
        )
    )

    # Summary of Hansard index
    tab1, tab2 = st.tabs(["Search", "Settings"])

    # daily_activity, bills = requests.get(f"{BACKEND_URL}/parlex/summary").json()

    with tab2:
        with st.expander("Show contributions over time"):
            pass

    with tab1:
        use_example_bill = st.toggle(
            "Use an example bill rather than entering your own topic",
            value=bool(st.session_state.get("parlex_by_mp_search_topic")),
        )

        if use_example_bill:
            selected_bill = st.selectbox("Choose a bill", [], format_func=lambda x: x["title"])
            st.write(f"{selected_bill['description']} {selected_bill['link']}")
            bill_summary = selected_bill["summary"]

            with st.expander("Bill summary", expanded=True):
                st.markdown(bill_summary)
        else:
            bill_summary = st.text_area(
                label="Provide your topic. More detail will result in an improved result. For a detailed query include the policy areas, aims, and effects along with other relevant information.",
                value=st.session_state.get("parlex_by_mp_search_topic"),
                placeholder="Enter the topic here...",
                key="bill_summary",
                height=150,
            )

        if st.session_state.get("bill_summary") != bill_summary:
            st.session_state.bill_summary = bill_summary

        num_contributions = st.session_state.get("num_contributions", 150)
        num_contributions = st.number_input(
            "Number of contributions to analyse (looks at the top N most relevant)",
            min_value=1,
            max_value=1000,
            value=num_contributions,
            key="num_contributions",
        )

        run_analysis_button = st.button("Run analysis")

        st.session_state.parlex_containers = {
            "error": st.empty(),
            "heading": st.empty(),
            "progress": st.empty(),
            "histogram": st.empty(),
            "filters": st.empty(),
            "subgroups": st.empty(),
            "contributions": st.empty(),
        }

        if st.session_state.get("contributions") is not None:
            with st.session_state.parlex_containers["contributions"]:
                with st.container():
                    st.subheader("Member Contributions")
                    with st.container(border=True):
                        for contribution in st.session_state.contributions.contributions:
                            display_contribution(contribution)

        if run_analysis_button:
            if not bill_summary:
                with st.session_state.parlex_containers["error"]:
                    st.error("Please provide a topic to analyse.")
                return None

            with st.session_state.parlex_containers["heading"]:
                st.subheader("Member summary")
            st.session_state.parlex_containers["contributions"].empty()
            st.session_state.contributions = ContributionData(bill_summary)

            st.write_stream(load_contributions(num_contributions, month_range=("June 2009", "July 2023")))


if __name__ == "__main__":
    research_by_topic()
