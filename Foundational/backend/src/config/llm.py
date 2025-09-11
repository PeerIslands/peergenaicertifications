from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import dotenv
import os

dotenv.load_dotenv()

if not os.environ["AZURE_OPENAI_ENDPOINT"]:
    raise ValueError("OPENAI_API_KEY environment variable is required")

model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

embeddings = AzureOpenAIEmbeddings(
    model=os.environ["EMBEDDING_MODEL"]
)


def get_embedding_model():
    """Get the embeddings model."""
    return embeddings

def get_llm_model():
    """Get the llm model."""
    return model