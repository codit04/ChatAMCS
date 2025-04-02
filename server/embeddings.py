import os
import json
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import PyPDF2
from datetime import  datetime
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

embeddings = OpenAIEmbeddings(openai_api_key=api_key)

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

    text += f"Brief Profile: {faculty['in_brief']}\n"


    if isinstance(faculty['research_areas'], list):
        text += f"Research Areas: {', '.join(faculty['research_areas'])}\n"
    else:
        text += f"Research Areas: {faculty['research_areas']}\n"

    if isinstance(faculty['subject_expertise'], list):
        text += f"Subject Expertise: {', '.join(faculty['subject_expertise'])}\n"
    else:
        text += f"Subject Expertise: {faculty['subject_expertise']}\n"


    text += "Selected Publications:\n"
    for i, pub in enumerate(faculty['publications']):
        if isinstance(pub, dict):
            text += f"- {pub.get('title', 'Unknown')} ({pub.get('year', 'Unknown')})\n"
        else:
            text += f"- {pub}\n"

    return text


def create_placement_text(path):
    #read text from pdf at path
    text = ""

    try:
        # Open the PDF file in binary read mode
        with open(path, 'rb') as file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)

            # Get the number of pages in the PDF
            num_pages = len(pdf_reader.pages)

            # Extract text from each page
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

            return text

    except FileNotFoundError:
        return f"Error: File not found at {path}"
    except Exception as e:
        return f"Error: {str(e)}"


def load_regulations_data(directory):
    regulations_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                try:
                    regulations_data.append(json.load(file))
                    print(f"Loaded {filename}")
                except json.JSONDecodeError:
                    print(f"Error loading {filename}: Invalid JSON")
    return regulations_data


def create_course_text(course):
    text = f"Code: {course.get('code', 'Unknown')}\n"
    text += f"Title: {course.get('title', 'Unknown')}\n"
    text += f"Credits: {course.get('credits', 'Unknown')}\n"

    if 'prerequisites' in course:
        text += "Prerequisites:\n"
        for prereq in course['prerequisites']:
            text += f"- {prereq}\n"

    if 'content' in course:
        text += "Course Content:\n"
        for section in course['content']:
            text += f"- {section['title']}: {section['content']}\n"

    if 'textbooks' in course:
        text += "Textbooks:\n"
        for book in course['textbooks']:
            text += f"- {book}\n"

    if 'references' in course:
        text += "References:\n"
        for ref in course['references']:
            text += f"- {ref}\n"

    return text


def create_regulation_text(regulation):
    text = f"Program: {regulation.get('program_name', 'Unknown')}\n"
    text += f"Year: {regulation.get('year', 'Unknown')}\n"
    text += f"Coordinator: {regulation.get('coordinator', 'Unknown')}\n"
    text += f"URL: {regulation.get('url', 'Unknown')}\n\n"

    text += "Courses:\n"
    for course in regulation.get('courses', []):
        text += "\n" + "-" * 50 + "\n"
        text += create_course_text(course)

    return text


def create_publication_text(file_path):
    # Read JSON data from the file
    with open(file_path, 'r') as file:
        publication_data = json.load(file)

    text = "Publications:\n\n"

    # Books section
    text += "BOOKS:\n" + "=" * 50 + "\n"
    for book in publication_data.get('publications', {}).get('books', []):
        text += f"Title: {book.get('title', 'Unknown')}\n"
        text += f"Author: {book.get('author', 'Unknown')}\n"
        if book.get('co_authors'):
            text += f"Co-Authors: {book.get('co_authors', 'Unknown')}\n"
        text += f"Publisher: {book.get('publisher', 'Unknown')}\n"
        text += f"Year: {book.get('year', 'Unknown')}\n"
        text += "-" * 50 + "\n"

    # Contributions section
    text += "\nCONTRIBUTIONS:\n" + "=" * 50 + "\n"
    for contrib in publication_data.get('publications', {}).get('contributions', []):
        text += f"Title: {contrib.get('title', 'Unknown')}\n"
        text += f"Nature: {contrib.get('nature', 'Unknown')}\n"
        text += f"Author: {contrib.get('author', 'Unknown')}\n"
        if contrib.get('contributor'):
            text += f"Contributor: {contrib.get('contributor', 'Unknown')}\n"
        text += f"Date: {contrib.get('date', 'Unknown')}\n"
        text += "-" * 50 + "\n"

    return text


def create_conference_text(file_path):
    # Read JSON data from the file
    with open(file_path, 'r') as file:
        conference_data = json.load(file)

    text = "Publications:\n\n"

    # International Conferences section
    text += "INTERNATIONAL CONFERENCES:\n" + "=" * 50 + "\n"
    for conf in conference_data.get('publications', {}).get('international_conferences', []):
        text += f"Title: {conf.get('title', 'Unknown')}\n"
        text += f"Author: {conf.get('author', 'Unknown')}\n"
        if conf.get('co_authors'):
            text += f"Co-Authors: {conf.get('co_authors', 'Unknown')}\n"
        text += f"Conference: {conf.get('conference', 'Unknown')}\n"
        text += f"Year: {conf.get('year', 'Unknown')}\n"
        text += "-" * 50 + "\n"

    # National Conferences section
    text += "\nNATIONAL CONFERENCES:\n" + "=" * 50 + "\n"
    for conf in conference_data.get('publications', {}).get('national_conferences', []):
        text += f"Title: {conf.get('title', 'Unknown')}\n"
        text += f"Author: {conf.get('author', 'Unknown')}\n"
        if conf.get('co_authors'):
            text += f"Co-Authors: {conf.get('co_authors', 'Unknown')}\n"
        text += f"Conference: {conf.get('conference', 'Unknown')}\n"
        text += f"Year: {conf.get('year', 'Unknown')}\n"
        text += "-" * 50 + "\n"

    return text


def create_conference_attended_text(file_path):
    # Read JSON data from the file
    with open(file_path, 'r') as file:
        conference_data = json.load(file)

    text = "Conference Attendance:\n\n"

    # Process each conference entry
    for conf in conference_data:
        text += "=" * 50 + "\n"
        text += f"Title: {conf.get('title', 'Unknown')}\n"
        text += f"Faculty: {conf.get('faculty', 'Unknown')}\n"
        text += f"Duration: {conf.get('from', 'Unknown')} to {conf.get('to', 'Unknown')}\n"
        text += f"Sponsoring Agencies: {conf.get('sponsoring_agencies', 'Unknown')}\n"
        text += "-" * 50 + "\n"

    return text


def create_events_organized_text(file_path):
    # Read JSON data from the file
    with open(file_path, 'r') as file:
        events_data = json.load(file)

    text = "Events Organized:\n\n"
    current_date = datetime.strptime("02-04-2025", "%d-%m-%Y")

    # Process each event entry
    for event in events_data.get('events_organized', []):
        text += "=" * 50 + "\n"
        text += f"Serial Number: {event.get('serial_number', 'Unknown')}\n"
        text += f"Title: {event.get('title', 'Unknown')}\n"
        text += f"Level: {event.get('level', 'Unknown')}\n"
        text += f"Nature: {event.get('nature', 'Unknown')}\n"

        if event.get('convener'):
            text += f"Convener: {event.get('convener', 'Unknown')}\n"

        if event.get('organizers') and len(event.get('organizers', [])) > 0:
            text += "Organizers:\n"
            for organizer in event.get('organizers', []):
                text += f"- {organizer}\n"

        # Parse dates to determine if event is past, current, or future
        start_date_str = event.get('start_date', 'Unknown')
        end_date_str = event.get('end_date', 'Unknown')

        if start_date_str != 'Unknown' and end_date_str != 'Unknown':
            try:
                start_date = datetime.strptime(start_date_str, "%d-%b-%Y")
                end_date = datetime.strptime(end_date_str, "%d-%b-%Y")

                if end_date < current_date:
                    status = "Completed"
                elif start_date <= current_date <= end_date:
                    status = "Ongoing"
                else:
                    status = "Upcoming"

                text += f"Duration: {start_date_str} to {end_date_str} ({status})\n"
            except ValueError:
                text += f"Duration: {start_date_str} to {end_date_str}\n"
        else:
            text += f"Duration: {start_date_str} to {end_date_str}\n"

        if event.get('sponsoring_agency'):
            text += f"Sponsoring Agency: {event.get('sponsoring_agency', 'Unknown')}\n"

        text += "-" * 50 + "\n"

    return text


def create_journal_publications_text(file_path):
    # Read JSON data from the file
    with open(file_path, 'r') as file:
        publications_data = json.load(file)

    text = "Journal Publications:\n\n"
    current_date = datetime.strptime("02-04-2025", "%d-%m-%Y")

    # Process each journal publication entry
    for pub in publications_data.get('publications', {}).get('international_journals', []):
        text += "=" * 50 + "\n"
        text += f"Title: {pub.get('title', 'Unknown')}\n"
        text += f"Author: {pub.get('author', 'Unknown')}\n"
        if pub.get('co_author'):
            text += f"Co-Author(s): {pub.get('co_author', 'Unknown')}\n"
        text += f"Publisher: {pub.get('publisher', 'Unknown')}\n"

        year = pub.get('year', 'Unknown')
        if year != 'Unknown':
            try:
                pub_year = int(year)
                if pub_year < current_date.year:
                    status = "Published"
                elif pub_year == current_date.year:
                    status = "Current"
                else:
                    status = "Upcoming"
                text += f"Year: {year} ({status})\n"
            except ValueError:
                text += f"Year: {year}\n"
        else:
            text += f"Year: {year}\n"

        text += "-" * 50 + "\n"

    return text


def create_labs_text(file_path):
    # Read JSON data from the file
    with open(file_path, 'r') as file:
        labs_data = json.load(file)

    text = "Laboratory Facilities:\n\n"

    # Process each lab entry
    for lab_name, lab_info in labs_data.items():
        text += "=" * 50 + "\n"
        text += f"Name: {lab_name}\n"

        if lab_info.get('Details'):
            text += f"Details: {lab_info.get('Details')}\n"

        if lab_info.get('Staff incharge'):
            text += f"Staff In-charge: {lab_info.get('Staff incharge')}\n"

        if lab_info.get('Location'):
            text += f"Location: {lab_info.get('Location')}\n"

        text += "-" * 50 + "\n"

    return text


def create_phd_completed_text(file_path):
    # Read JSON data from the file
    with open(file_path, 'r') as file:
        phd_data = json.load(file)

    text = "PhD Completions:\n\n"

    # Process each PhD completion entry
    for phd in phd_data.get('phd_completed', []):
        text += "=" * 50 + "\n"

        candidate_num = phd.get('candidate', 'Unknown')
        candidate_name = phd.get('thesis_title', 'Unknown')
        thesis_title = phd.get('guide', 'Unknown')
        guide = phd.get('completion_date', 'Unknown')

        text += f"Candidate Number: {candidate_num}\n"
        text += f"Candidate Name: {candidate_name}\n"
        text += f"Thesis Title: {thesis_title}\n"
        text += f"Guide: {guide}\n"

        text += "-" * 50 + "\n"

    return text

# Load faculty data
faculty_data = load_faculty_data("/Users/codit/PycharmProjects/ChatAMCS/data/faculty_data")
regulation_data = load_regulations_data("/Users/codit/PycharmProjects/ChatAMCS/data/regulations")
print(f"Loaded {len(faculty_data)} faculty profiles")
print(f"Loaded {len(regulation_data)} regulation profiles")

# Create documents for FAISS
documents = []
for faculty in faculty_data:
    text = create_faculty_text(faculty)
    doc = Document(page_content=text, metadata={"name": faculty.get('name', 'Unknown')})
    documents.append(doc)

for regulation in regulation_data:
    text = create_regulation_text(regulation)
    doc = Document(page_content=text, metadata={"name": regulation.get('Program', 'Unknown')})
    documents.append(doc)

text = create_placement_text('/Users/codit/PycharmProjects/ChatAMCS/data/placement/MSc_Brochure_2023.pdf')
doc = Document(page_content=text, metadata={"name": 'Placement Data'})
documents.append(doc)

print("Loaded Placement details")

text = create_publication_text('/Users/codit/PycharmProjects/ChatAMCS/data/book.json')
doc = Document(page_content=text, metadata={"name": 'Publication Data'})
documents.append(doc)
print("Loaded Publication details")

text = create_conference_text('/Users/codit/PycharmProjects/ChatAMCS/data/Conference_Publications.json')
doc = Document(page_content=text, metadata={"name": 'Conference Data'})
documents.append(doc)
print("Loaded Conference Publication details")

text = create_conference_attended_text('/Users/codit/PycharmProjects/ChatAMCS/data/conferences.json')
doc = Document(page_content=text, metadata={"name": 'Conference Attended'})
documents.append(doc)
print("Loaded Conference Attended details")

text = create_events_organized_text('/Users/codit/PycharmProjects/ChatAMCS/data/Events_Organized.json')
doc = Document(page_content=text, metadata={"name": 'Events Organized'})
documents.append(doc)
print("Loaded Events Organized details")

text = create_journal_publications_text('/Users/codit/PycharmProjects/ChatAMCS/data/Journal_Publication.json')
doc = Document(page_content=text, metadata={"name": 'Journal Publications'})
documents.append(doc)
print("Loaded Journal Publications details")

text = create_labs_text('/Users/codit/PycharmProjects/ChatAMCS/data/labs.json')
doc = Document(page_content=text, metadata={"name": 'Laboratory Facilities'})
documents.append(doc)
print("Loaded Laboratory Facilities details")

text = create_phd_completed_text('/Users/codit/PycharmProjects/ChatAMCS/data/phd.json')
doc = Document(page_content=text, metadata={"name": 'PhD Completed'})
documents.append(doc)
print("Loaded PhD Completed details")

print(f"Created {len(documents)} documents")

# Create FAISS index
vectorstore = FAISS.from_documents(documents, embeddings)

#Save the FAISS index
vectorstore.save_local("server/faiss_index")

print("FAISS index created and saved successfully.")
