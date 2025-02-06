import logging
import os

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import AuthenticationException
from langchain.prompts import PromptTemplate
from openai import AzureOpenAI

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  # Enable debug logging


def get_elasticsearch_client() -> Elasticsearch:
    """Returns an Elasticsearch client."""

    cloud_id = os.environ.get("ELASTICSEARCH_CLOUD_ID").replace("'", "")
    api_key = os.environ.get("ELASTICSEARCH_API_KEY").replace("'", "")

    client = Elasticsearch(
        cloud_id=cloud_id,
        api_key=api_key
    )

    try:
        client.info()
        logger.info("Connected to Elasticsearch")
        return client
    except AuthenticationException as e:
        logger.error(f"Authentication error connecting to Elasticsearch: {e}")
        return None
    except Exception as e:
        logger.error(f"Error connecting to Elasticsearch: {e}")
        return None

def get_openai_client():

    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT").replace("'", "")
    api_key=os.environ.get("AZURE_OPENAI_API_KEY").replace("'", "")
    api_version= os.environ.get("OPENAI_API_VERSION").replace("'", "") # "2024-08-01-preview"

    return AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version
    )

def load_prompt_template(filename):
    """
    Load a prompt template from a .txt file in the prompts directory.

    Args:
        filename (str): Name of the file (with .txt extension) in the prompts directory

    Returns:
        PromptTemplate: A LangChain prompt template
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dir = os.path.join(current_dir, "prompts")
    file_path = os.path.join(prompt_dir, filename)

    with open(file_path, "r") as f:
        template = f.read().strip()

    return PromptTemplate(template=template)
