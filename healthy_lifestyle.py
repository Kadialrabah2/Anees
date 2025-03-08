from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
import os
def initialize_llm():
  llm = ChatGroq(
    temperature = 0,
    groq_api_key = "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",
    model_name = "llama-3.3-70b-versatile"
)
  return llm

def create_vector_db():

  data_path = os.path.join(os.getcwd(), "data")  # Get the correct path
  loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls=PyPDFLoader)

  documents = loader.load()
  text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
  texts = text_splitter.split_documents(documents)
  embeddings = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-MiniLM-L6-v2')
  vector_db = Chroma.from_documents(texts, embeddings, persist_directory = './chroma_db')
  vector_db.persist()

  print("ChromaDB created and data saved")

  return vector_db

def setup_qa_chain(vector_db, llm):
  retriever = vector_db.as_retriever()
  memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")
  prompt_templates = """ You are a health and wellness expert, guiding users to improve their mental and physical well-being through healthy daily habits. 
Your responses should be practical, personalized, and encouraging, covering key aspects of a balanced lifestyle: 
nutrition, hydration, sleep hygiene, and daily routines. Provide science-backed advice and simple strategies that users can easily incorporate into their lives.

Focus on creating a supportive, non-judgmental tone to motivate users to make small, sustainable changes. Offer actionable tips on:
- Healthy eating habits that promote energy and mental clarity.
- Staying hydrated and the importance of water intake for overall well-being.
- Creating a healthy sleep routine to improve rest and mental health.
- Building daily routines that balance productivity, physical activity, and relaxation.

Be empathetic and adjust your advice based on the user’s preferences, challenges, and goals. Remind users that their health journey is unique and that it’s okay to take small steps toward improvement.

**Previous Conversation History:**
    {chat_history}

**Context (What you know):**
{context}

**User Question:**
{question}

**Chatbot Response (in the same language as the user’s input):** """
  PROMPT = PromptTemplate(template=prompt_templates, input_variables=['chat_history', 'context', 'question'])

  qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT, "memory": memory}
    )
    
  return qa_chain


def main():
  print("Intializing Chatbot.........")
  llm = initialize_llm()

  db_path = "/content/chroma_db"

  if not os.path.exists(db_path):
    vector_db  = create_vector_db()
  else:
    embeddings = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-MiniLM-L6-v2')
    vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
  qa_chain = setup_qa_chain(vector_db, llm)

  while True:
    query = input("\nHuman: ")
    if query.lower()  == "exit":
      print("Chatbot: Take Care of yourself, Goodbye!")
      break
    response = qa_chain.run(query)
    print(f"Chatbot: {response}")

if __name__ == "__main__":
  main()