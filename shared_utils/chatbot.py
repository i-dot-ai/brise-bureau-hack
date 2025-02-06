import openai
import os
from openai import AzureOpenAI
import logging
from shared_utils.schema import chatBotDecision, ProcessMap
from shared_utils.prompts import get_process_mapping_prompt


import openai
import os
from openai import AzureOpenAI
from shared_utils.schema import chatBotDecision, ProcessMap, chatBotMessage, addEdgeDecision, addNodeDecision
from shared_utils.prompts import get_process_mapping_prompt
import streamlit as st

class Chatbot:
    def __init__(self):
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT").replace("'", "")
        api_key=os.environ.get("AZURE_OPENAI_API_KEY").replace("'", "")
        api_version= os.environ.get("OPENAI_API_VERSION").replace("'", "") # "2024-08-01-preview"

        AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )

        self.conversation = []


    def get_response(self, user_input, process_map: ProcessMap):
        st.session_state.conversation.append({"role": "user", "content": user_input})

        # Prepare messages for the API call
        messages = [{"role": "system", "content": get_process_mapping_prompt(process_map)}]
        messages.extend(st.session_state.conversation)

        # Generate a response using OpenAI's new API
        # response = openai.chat.completions.create(
        #     model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME").replace("'", ""),
        #     messages=messages
        # )
        print("These are the messages: ", messages)
        completion = openai.beta.chat.completions.parse(
            model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME").replace("'", ""),
            messages=messages,
            response_format=chatBotDecision,
        )

        bot_response: chatBotDecision = completion.choices[0].message.parsed
        # TODO: GCLOMAX - append to the conversation in plaintext. 
        for response in bot_response:
            if isinstance(response, chatBotMessage):
                st.session_state.conversation.append({"role": "assistant", "content": response.content})
            elif isinstance(response, addEdgeDecision):
                text_string= "Bot added an edge: {}".format(response.edge)
                st.session_state.conversation.append({"role": "assistant", "content": text_string})
            elif isinstance(response, addNodeDecision):
                text_string= "Bot added a node: {}".format(response.node)
                st.session_state.conversation.append({"role": "assistant", "content": text_string})

        return bot_response
    
    def get_process_map_initial(self, uploaded_file):

        # Prepare messages for the API call
        messages = [{"role": "system", "content": f"Build a process map adding nodes or edges until finished. Use the format {ProcessMap}"}]
        messages.append({"role": "user", "content": uploaded_file})

        completion = openai.beta.chat.completions.parse(
            model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME").replace("'", ""),
            messages=messages,
            response_format=ProcessMap,
        )

        bot_response = completion.choices[0].message.parsed
        # TODO: GCLOMAX - append to the conversation in plaintext.
        return bot_response



class Summariser:
    def __init__(self):
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT").replace("'", "")
        api_key=os.environ.get("AZURE_OPENAI_API_KEY").replace("'", "")
        api_version= os.environ.get("OPENAI_API_VERSION").replace("'", "") # "2024-08-01-preview"

        AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version
        )

        self.conversation = []


    def get_summary(self, user_input, number_of_documents, language="en"):
        # Generate a response using OpenAI's new API
        if language == "en":
            messages = [{"role": "system", "content": "The following is set of documents uploaded by a user. Please read each document in turn and summarise the key points in under 100 words."}]
        else:
            messages = [{"role": "system", "content": "You are a helpful english to french translater and summariser. The following is set of documents uploaded by a user. Please read each document which is in English and in turn and summarise the key points in under 100 words in French."}]

        messages.append({"role": "system", "content": f"Number of documents: {number_of_documents}"})
        messages.append({"role": "user", "content": user_input})

        response = openai.chat.completions.create(
            model=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME").replace("'", ""),
            messages=messages,
        )
        return response.choices[0].message.content
