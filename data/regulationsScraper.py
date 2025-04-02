from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import json
import re

# Create necessary directories
os.makedirs('regulations', exist_ok=True)


def extract_program_info(html_content, program_name, year):
    """Extract program information from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')

    program_info = {
        'program_name': program_name,
        'year': year,
        'courses': []
    }

    # Extract all section elements which contain course information
    sections = soup.find_all('section', class_='section')

    for section in sections:
        course_info = {}

        # Extract course code and title
        heading = section.find('h3')
        if heading:
            course_title = heading.text.strip()
            # Extract course code using regex (assuming format like "20XT11")
            code_match = re.search(r'(\d+[A-Z]+\d+)', course_title)
            if code_match:
                course_code = code_match.group(1)
                course_info['code'] = course_code
                course_info['title'] = course_title.replace(course_code, '').strip()

                # Determine course type based on code pattern
                if re.match(r'\d{2}[A-Z]{2}\d{2}', course_code):
                    # Pattern like 20XT11 - regular course
                    semester_match = re.match(r'\d{2}[A-Z]{2}(\d)(\d)', course_code)
                    if semester_match:
                        course_info['semester'] = int(semester_match.group(1))
                        course_info['course_type'] = 'regular'
                elif re.match(r'\d{2}[A-Z]{2}[E|A]\d', course_code):
                    # Pattern like 20XTE1 or 20XTA1 - professional elective
                    course_info['course_type'] = 'professional_elective'
                elif re.match(r'\d{2}[A-Z]{2}O\d', course_code):
                    # Pattern like 20XTO1 - open elective
                    course_info['course_type'] = 'open_elective'
            else:
                course_info['title'] = course_title

        # Extract credit information
        credit_info = section.find('p', style='text-align:right')
        if credit_info and not credit_info.text.startswith('Total'):
            course_info['credits'] = credit_info.text.strip()

        # Extract prerequisites if any
        prereq_section = section.find('p', style='background-color: #92a8d1;color:white')
        if prereq_section:
            prereq_items = prereq_section.find_all('li')
            prerequisites = []
            for item in prereq_items:
                prereq_text = item.text.strip()
                # Check if there's a link to another course
                prereq_link = item.find('a')
                if prereq_link:
                    linked_course = prereq_link.text.strip()
                    linked_code = prereq_link.get('href')
                    if linked_code:
                        linked_code = linked_code.replace('#a', '')
                    prerequisites.append({
                        'course': linked_course,
                        'code': linked_code
                    })
                else:
                    prerequisites.append(prereq_text)

            if prerequisites:
                course_info['prerequisites'] = prerequisites

        # Extract course content
        content_paragraphs = []
        for p in section.find_all('p'):
            # Skip already processed paragraphs
            if p == credit_info or (prereq_section and p == prereq_section):
                continue

            # Check if this is a content paragraph with a bold title
            if p.find('b'):
                section_title = p.find('b').text.strip()

                # Skip if this is textbooks or references section that will be processed separately
                if section_title in ['TEXT BOOKS:', 'REFERENCES:', 'TUTORIAL PRACTICE:']:
                    continue

                section_content = p.text.replace(section_title, '', 1).strip()
                content_paragraphs.append({
                    'title': section_title,
                    'content': section_content
                })

        if content_paragraphs:
            course_info['content'] = content_paragraphs

        # Extract textbooks
        textbooks = []
        for p in section.find_all('p'):
            if p.find('b') and 'TEXT BOOKS:' in p.find('b').text:
                # Get the text content after the "TEXT BOOKS:" heading
                text = p.get_text(separator='\n')
                if 'TEXT BOOKS:' in text:
                    textbooks_part = text.split('TEXT BOOKS:')[1]
                    if 'REFERENCES:' in textbooks_part:
                        textbooks_part = textbooks_part.split('REFERENCES:')[0]

                    # Extract numbered items
                    for line in textbooks_part.split('\n'):
                        if line.strip() and re.match(r'^\d+\.', line.strip()):
                            textbooks.append(line.strip())

        if textbooks:
            course_info['textbooks'] = textbooks

        # Extract references
        references = []
        for p in section.find_all('p'):
            if p.find('b') and 'REFERENCES:' in p.find('b').text:
                # Get the text content after the "REFERENCES:" heading
                text = p.get_text(separator='\n')
                if 'REFERENCES:' in text:
                    references_part = text.split('REFERENCES:')[1]

                    # Extract numbered items
                    for line in references_part.split('\n'):
                        if line.strip() and re.match(r'^\d+\.', line.strip()):
                            references.append(line.strip())

        if references:
            course_info['references'] = references

        # Add course to program courses if we have meaningful data
        if course_info and 'title' in course_info:
            program_info['courses'].append(course_info)

    return program_info


def scrape_program_syllabus(url, program_name, year):
    """Scrape a program syllabus using Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            html_content = page.content()
            program_info = extract_program_info(html_content, program_name, year)
            program_info['url'] = url

            # Save the extracted information as JSON
            filename = f"regulations/{program_name.replace(' ', '_')}_{year}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(program_info, f, indent=4)

            print(f"Successfully extracted information for {program_name} ({year})")
            print(f"Data saved to {filename}")

            return program_info

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
        finally:
            browser.close()


def main():
    # Create directory for storing data
    os.makedirs('regulations', exist_ok=True)

    # Load regulations data from JSON file
    try:
        with open('regulations.json', 'r', encoding='utf-8') as f:
            regulations_data = json.load(f)

        print(f"Loaded regulations data for {len(regulations_data)} programs")

        # Process each program
        for program_name, program_details in regulations_data.items():
            coordinator = program_details.get('Program Co-ordinator', 'Not specified')
            years = program_details.get('Year', [])
            urls = program_details.get('url', [])

            print(f"\nProcessing {program_name}")
            print(f"Coordinator: {coordinator}")

            # Process each year/URL combination
            for i in range(min(len(years), len(urls))):
                year = years[i]
                url = urls[i]

                print(f"Scraping syllabus for year {year} from {url}")
                program_info = scrape_program_syllabus(url, program_name, year)

                if program_info:
                    # Add coordinator information
                    program_info['coordinator'] = coordinator

                    # Update the saved JSON with coordinator info
                    filename = f"regulations/{program_name.replace(' ', '_')}_{year}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(program_info, f, indent=4)

    except FileNotFoundError:
        print("Error: regulations.json file not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in regulations.json file.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
