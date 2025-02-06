import asyncio
from datetime import datetime
from itertools import groupby
import json
import logging
import os
from typing import Any, AsyncIterator

from pydantic import BaseModel, Field
from openai import AsyncAzureOpenAI
import openai

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MAX_CONCURRENT_OPENAI_REQUESTS = 20
MEMBER_SUMMARY_TIMEOUT = 10

SUMMARY_SYSTEM_PROMPT = """
You are an expert in analysing contributions to the EU parliament and using that to make an informed judgement about a members likely sentiment towards a topic.

You will be provided with a topic, bill, or policy and a list of contributions that a member of parliament has made related to this topic. Given this information, your task is to make an informed judgement of how this member may respond to the new topic, bill, or policy.

The user is most interested in recent information about the Member of Parliament. The date today is {date_today}. You should use this to make an informed judgement about which information is most relevant. For example if the user is interested in a topic that a member has spoken about in the last few months and four years ago, then the recent information is much more useful.

You will use the following framework to analyse the contributions:

- 1. **Key Themes and Concerns**: Identify key themes and concerns raised by the member in their relevant contributions that overlap or align with the new bill.
- 2. **Background Alignment**: Evaluate how the members background is aligned with or diverge from the topic's objectives.
- 3. **Tone and Sentiment**: Analyse the tone and sentiment of their contributions and how it might reflect their position on the new bill.
---

## Start of Topic, Bill, or Policy

{topic_query}
---
"""

SUMMARY_USER_PROMPT = """
## Member Background

{member_background}

## Relevant Contributions

{combined_contributions}
"""


async def filter_nones_from_stream(stream: AsyncIterator[Any]) -> AsyncIterator[Any]:
    async for item in stream:
        if item is not None:
            yield item


def get_eu_parliament_query_body(query_string, doc_limit, date_range):
    # TODO: add date range filter
    return {
        "query": {"semantic": {"field": "speech_text", "query": query_string}},
        "size": doc_limit,
        "_source": [
            "speech_text.text",
            "speaker_name",
            "speaker_party",
            "speaker_role",
            "debate_title",
            "date",
        ],
    }


def format_member_details(contributions, speaker_name):
    contributing_member = {
        "member_id": speaker_name,
        "member_contribution_count": len(contributions),
        "member_avg_score": 1,
        "contributions": [],
    }
    for contribution in contributions:
        source = contribution
        contribution = {
            "member_id": speaker_name,
            "member_name": source["speaker_name"],
            # TODO: move this data in ingestion to the member rather than the contribution
            "member_party_name": source.get("speaker_party", "Unknown"),
            "member_party_abbreviation": source.get("speaker_role", "Unknown"),
            "member_party_foreground_colour": "0022CC",
            "member_party_background_colour": "0022CC",
            "member_house_background_colour": "b50938",
            "member_url": f"NA",
            "member_contribution_count": len(contributions),
            "member_avg_score": 1,
            "text": source["speech_text"]["text"],
            "attributed_to": source["speaker_name"],
            "house": contribution.get("house", "Unknown"),
            "date": source["date"],
            "score": 1,
            "contribution_url": f"NA",
            "debate_url": f"NA",
            "debate_title": source["debate_title"],
            "chamber_date_url": f"NA",  # gets the date part of the datetime
        }
        contributing_member["contributions"].append(contribution)

    return contributing_member


async def parlex_query_eu_parliament(
    es_client,
    openai_client,
    query,
    date_range: tuple[datetime.date, datetime.date],
    doc_limit=100,
):
    # set up tracking variables
    tasks = []
    max_contributions = 0

    index_name = "markd-paris-hack-eu-speeches"
    response = es_client.search(
        index=index_name,
        body=get_eu_parliament_query_body(query, doc_limit, date_range),
        request_timeout=60,
    )
    eu_response = [hit["_source"] for hit in response["hits"]["hits"]]
    for item in eu_response:
        item["house"] = "EU Parliament"

    index_name = "livlivesey_paris_hack_fr_debates_0602"
    response = es_client.search(
        index=index_name,
        body=get_eu_parliament_query_body(query, doc_limit, date_range),
        request_timeout=60,
    )
    fr_response = [hit["_source"] for hit in response["hits"]["hits"]]
    for item in fr_response:
        item["house"] = "French National Assembly"

    response = eu_response + fr_response
    response = groupby(
        sorted(response, key=lambda x: x["speaker_name"]),
        key=lambda x: x["speaker_name"],
    )

    # for each active parliamentarian, reformat response data
    for speaker_name, contributions in response:
        contributions = list(contributions)
        contributing_member = format_member_details(contributions, speaker_name)

        tasks.append(add_summary_to_member(openai_client, contributing_member, speaker_name, query))

        max_contributions = max(max_contributions, len(contributing_member["contributions"]))

    # send summary information to the frontend
    yield (
        json.dumps(
            {
                "message_type": "summary",
                "number_results": len(tasks),
                "max_contributions": max_contributions,
            }
        )
        + "\n"
    )

    # when llm summaries have been prepared for each parliamentarian, send to frontend
    for task in asyncio.as_completed(tasks):
        try:
            result = await asyncio.wait_for(task, timeout=MEMBER_SUMMARY_TIMEOUT)
            yield (json.dumps({"message_type": "contribution", "contribution": result}) + "\n")
        except asyncio.TimeoutError:
            logger.warning(f"Task timed out after {MEMBER_SUMMARY_TIMEOUT} seconds")
            yield None
        except Exception as e:
            logger.exception(f"Error processing task: {str(e)}")
            yield None


async def add_summary_to_member(openai_client, member_dict, member_id, bill_summary):
    summary = await summarise_member_position(openai_client, member_dict["contributions"], member_id, bill_summary)
    member_dict["summary"] = summary["summary"]
    member_dict["headline"] = summary["headline"]
    member_dict["bill_sentiment"] = summary["bill_sentiment"]
    member_dict["indicative_quotes"] = summary["indicative_quotes"]
    return member_dict


async def summarise_member_position(
    openai_client: AsyncAzureOpenAI,
    member_contributions: list[dict],  # TODO: add more details
    member_id: int,
    bill_summary: str,
) -> dict:
    combined_contributions = get_combined_contributions(member_contributions)

    system_prompt = SUMMARY_SYSTEM_PROMPT.format(
        topic_query=bill_summary,
        date_today=datetime.now().strftime("%Y-%m-%d"),
    )

    user_prompt = SUMMARY_USER_PROMPT.format(
        member_background=member_id,
        combined_contributions=combined_contributions,
    )

    async with asyncio.Semaphore(MAX_CONCURRENT_OPENAI_REQUESTS):
        try:
            response_content = await openai_client.beta.chat.completions.parse(
                model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
                response_format=MemberSummaryResponse,
            )

        except openai.APIConnectionError as e:
            logger.error(f"Error in summarise_member_position: {e.__dict__}")

    response_content = response_content.choices[0].message.content

    try:
        response = MemberSummaryResponse.model_validate_json(response_content)
        response = response.model_dump()
    except Exception as e:
        # TODO: handle exceptions
        logger.error(f"Error in summarise_member_position: {e.__dict__}")
        logger.error(f"Response: {response_content}")
        raise

    return response


class MemberSummaryResponse(BaseModel):
    summary: str = Field(
        description="A summary of the member's position on the bill using the headings provided. Use markdown, but use bold text instead of heading tags for the headings."
    )
    headline: str = Field(description="A single line headline summarising the member's position on the new bill.")
    bill_sentiment: int = Field(
        description="Infer how the member may feel towards the new bill. Return the bill sentiment on a scale of 1 to 10, where 1 is strongly against, 5 is neutral or not applicable, and 10 is strongly for. Return this value as a single number."
    )
    indicative_quotes: list[str] = Field(
        description="A list of indicative quotes from the member's contributions that best capture their position and how it aligns with the new bill. Quote the relevant text exactly, retain capitalisation and do not add quotation marks etc."
    )


def get_combined_contributions(records) -> str:
    text = ""
    for record in records:
        text += f"\n\nContribution Date: {record['date']}"
        text += f"\nContribution House: {record['house']}"
        text += f"\nContribution part of debate: {record['debate_title']}"
        text += f"\nContribution:\n{record['text']}"

    return text
