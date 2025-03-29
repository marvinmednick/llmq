"""
LLM service implementations using LangChain.
"""

import os
import re
from pathlib import Path
from loguru import logger
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def get_llm_chain(service_type, prompt_path):
    """
    Get a LangChain chain for the specified service type.

    Args:
        service_type: Type of LLM service to use
        prompt_path: Path to the prompt template file

    Returns:
        LangChain chain
    """
    # Create LLM based on service type
    if service_type == "azure_openai":
        llm = get_azure_openai_llm()
    elif service_type == "openai":
        llm = get_openai_llm()
    else:
        raise ValueError(f"Unsupported service type: {service_type}")

    # Load prompt template
    with open(prompt_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Create LangChain prompt template
    # Convert {{variable}} to {variable} for LangChain
    langchain_template = re.sub(r"\{\{([a-zA-Z0-9_]+)\}\}\}", r"{\1}", template_content)
    langchain_template = re.sub(r"\{\{([a-zA-Z0-9_]+)\}\}", r"{\1}", langchain_template)

    # Extract input variables
    input_variables = re.findall(r"\{([a-zA-Z0-9_]+)\}", langchain_template)

    # Create prompt template
    prompt = PromptTemplate(
        template=langchain_template, input_variables=input_variables
    )

    # Create chain
    chain = RunnablePassthrough() | prompt | llm | StrOutputParser()

    return chain


def get_azure_openai_llm():
    """
    Get an Azure OpenAI LLM instance.

    Returns:
        AzureChatOpenAI instance
    """
    # Required environment variables
    required_vars = {
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
        "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    }

    # Check for missing environment variables
    missing_vars = [name for name, value in required_vars.items() if not value]

    if missing_vars:
        missing_list = ", ".join(missing_vars)
        raise ValueError(
            f"Missing required environment variables: {missing_list}\n"
            f"Please set these variables in your .env file or environment."
        )

    # Create Azure OpenAI LLM
    return AzureChatOpenAI(
        azure_deployment=required_vars["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=required_vars["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=required_vars["AZURE_OPENAI_ENDPOINT"],
        api_key=required_vars["AZURE_OPENAI_API_KEY"],
        temperature=0.7,
    )


def get_openai_llm():
    """
    Get an OpenAI LLM instance.

    Returns:
        ChatOpenAI instance
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing OPENAI_API_KEY environment variable.\n"
            "Please set this variable in your .env file or environment."
        )

    # Create OpenAI LLM
    return ChatOpenAI(model_name="gpt-4", temperature=0.7, api_key=api_key)
