import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure you have your OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings()

# Load your existing FAISS index
vectorstore = FAISS.load_local("server/faiss_index", embeddings, allow_dangerous_deserialization=True)

# Create a retriever with k=40 to get more context
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Define custom prompt templates
qa_prompt_template = """
You are a chat bot helping students of Applied Mathematics and Computational Sciences at PSG College of Technology who's head is Dr. Shina Sheen and director is Dr. Nadarajan R.
Use ONLY the following pieces of context to answer the question at the end.
If the information is not explicitly mentioned in the context, say "I don't have specific information about that."
Do not make up or infer information that is not directly stated in the context.

Context:
{context}

Question: {question}

Chat History:
{chat_history}

Answer:
"""

QA_PROMPT = PromptTemplate(
    template=qa_prompt_template,
    input_variables=["context", "question", "chat_history"]
)

# Initialize conversation memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

# Initialize GPT-4o model
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=1)

# Create the conversational chain
conversation_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": QA_PROMPT},
    return_source_documents=True
)


# Function to query the system
def answer_query(query):
    result = conversation_chain({"question": query})
    return {
        "answer": result["answer"],
        "source_documents": result["source_documents"]
    }


# Example usage
if __name__ == "__main__":
    print("Ask questions about professors or type 'exit' to quit.")

    while True:
        query = input("\nYour question: ")
        if query.lower() == 'exit':
            break

        response = answer_query(query)
        print("\nAnswer:", response["answer"])
        print("\nSources:")
        for i, doc in enumerate(response["source_documents"][:3]):  # Show only top 3 sources
            print(f"Source {i + 1}: {doc.metadata.get('name', 'Unknown')}")
