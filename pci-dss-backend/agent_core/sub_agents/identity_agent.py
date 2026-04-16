import os
import warnings
import pip_system_certs.wrapt_requests
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from api.schemas import ScanTrigger, ComplianceResponse
from langchain_openai import ChatOpenAI

load_dotenv()

def analyze_identity(trigger: ScanTrigger, iam_config: str) -> ComplianceResponse:
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../knowledge_base/faiss_db"))
    
    embeddings = CohereEmbeddings(
        cohere_api_key=os.getenv('COHERE_API_KEY'),
        model='embed-english-v3.0'
    )
    
    vectorstore = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
    
    query = f"IAM MFA password privileged access role PCI {trigger.pci_version}"
    docs = retriever.invoke(query)
    context = '\n'.join([d.page_content for d in docs])
    
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0
    )
    
    structured_llm = llm.with_structured_output(ComplianceResponse)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert PCI DSS IAM auditor. Check identity controls against the rules below.
        
        CRITICAL INSTRUCTIONS (OBEY STRICTLY):
        1. Only flag a "VIOLATION" if the config EXPLICITLY states a failure (e.g., 'MFA disabled', short passwords).
        2. If the config explicitly states a control is active (e.g., 'MFA enabled', 'Password: 14 chars'), you MUST assume it is fully compliant and output a "PASS" status.
        3. DO NOT assume a violation just because a specific word (like 'CDE access') is not mentioned in the short config string.
        4. If it is a violation, assign it to "Identity_Team". If it passes, set assigned_to to null.
        
        Return your analysis in the strict JSON schema provided."""),
        ("human", "PCI Rules:\n{context}\n\nIAM Config:\n{config}")
    ])
    
    chain = prompt | structured_llm
    
    return chain.invoke({
        'context': context, 
        'config': iam_config
    })