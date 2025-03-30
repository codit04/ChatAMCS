import os
import json
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Initialize OpenAI embeddings with the API key
embeddings = OpenAIEmbeddings(openai_api_key=api_key)

# Function to load faculty data from JSON files
def load_faculty_data(directory):
    faculty_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                try:
                    faculty_data.append(json.load(file))
                    print(f"Loaded {filename}")
                except json.JSONDecodeError:
                    print(f"Error loading {filename}: Invalid JSON")
    return faculty_data


# Function to create a text representation of faculty data
def create_faculty_text(faculty):
    text = f"Name: {faculty.get('name', 'Unknown')}\n"
    text += f"Academic Title: {faculty.get('academic_title', 'Unknown')}\n"
    text += f"Department: {faculty.get('department', 'Unknown')}\n"
    text += f"Email: {faculty.get('email', 'Unknown')}\n"
    text += f"Website: {faculty.get('url', 'Unknown')}\n"
    text += f"Qualification: {faculty.get('qualifications', 'Unknown')}\n"
    text += f"Joining Date: {faculty.get('joining_date', 'Unknown')}\n"
    text += f"Faculty ID: {faculty.get('faculty_id', 'Unknown')}\n"
    text += f"Google Scholar:{faculty.get('google_scholar','Unknown')}\n"
    # Add in brief section
    if 'in_brief' in faculty and faculty['in_brief']:
        text += f"Brief Profile: {faculty['in_brief']}\n"

    # Add research areas
    if 'research_areas' in faculty and faculty['research_areas']:
        if isinstance(faculty['research_areas'], list):
            text += f"Research Areas: {', '.join(faculty['research_areas'])}\n"
        else:
            text += f"Research Areas: {faculty['research_areas']}\n"

    # Add subject expertise
    if 'subject_expertise' in faculty and faculty['subject_expertise']:
        if isinstance(faculty['subject_expertise'], list):
            text += f"Subject Expertise: {', '.join(faculty['subject_expertise'])}\n"
        else:
            text += f"Subject Expertise: {faculty['subject_expertise']}\n"

    # Add publications (limited to first 5 for brevity)
    if 'publications' in faculty and faculty['publications']:
        text += "Selected Publications:\n"
        for i, pub in enumerate(faculty['publications']):
            if isinstance(pub, dict):
                text += f"- {pub.get('title', 'Unknown')} ({pub.get('year', 'Unknown')})\n"
            else:
                text += f"- {pub}\n"

    return text


# Load faculty data
faculty_data = load_faculty_data("/Users/codit/PycharmProjects/ChatAMCS/data/faculty_data")
print(f"Loaded {len(faculty_data)} faculty profiles")

# Create documents for FAISS
documents = []
for faculty in faculty_data:
    text = create_faculty_text(faculty)
    doc = Document(page_content=text, metadata={"name": faculty.get('name', 'Unknown')})
    documents.append(doc)

print(f"Created {len(documents)} documents")

# Create FAISS index
vectorstore = FAISS.from_documents(documents, embeddings)

#Save the FAISS index
vectorstore.save_local("server/faiss_index")

print("FAISS index created and saved successfully.")
