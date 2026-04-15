import os
import pip_system_certs.wrapt_requests
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from api.schemas import ScanTrigger, ComplianceResponse
from langchain_openai import ChatOpenAI

load_dotenv()

def analyze_infrastructure(trigger: ScanTrigger, mock_config: str) -> ComplianceResponse:
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../knowledge_base/faiss_db"))
    
    embeddings = CohereEmbeddings(
        cohere_api_key=os.getenv("COHERE_API_KEY"),
        model="embed-english-v3.0"
    )
    
    vectorstore = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    query = f"{trigger.cloud_provider} database encryption and access control PCI {trigger.pci_version}"
    docs = retriever.invoke(query)
    context = "\n".join([d.page_content for d in docs])
    
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0
    )
    
    structured_llm = llm.with_structured_output(ComplianceResponse)
    
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert PCI DSS auditor. Evaluate the server config against the PCI rules below.
        
        CRITICAL INSTRUCTIONS (OBEY STRICTLY):
        1. Only flag a "VIOLATION" if the config EXPLICITLY states a failure (e.g., 'PubliclyAccessible: True', 'StorageEncrypted: False').
        2. If the config states a control is secure (e.g., 'StorageEncrypted: True', 'PubliclyAccessible: False'), you MUST assume it is fully compliant and output a "PASS" status. Do not invent missing context.
        3. DO NOT assume a violation just because a specific rule detail (like logical access) is not mentioned in the config string.
        4. If it is a violation, assign it to "Cloud_Sec_Team". If it passes, set assigned_to to null.
        
        Return your analysis in the strict JSON schema provided."""),
        ("human", "PCI Rules:\n{context}\n\nServer Config:\n{config}\n\nSystem ID: {system_id}")
    ])
    
    chain = prompt | structured_llm
    
    return chain.invoke({
        "context": context,
        "config": mock_config,
        "system_id": trigger.system_id
    })