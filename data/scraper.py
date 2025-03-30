from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import json


# Create necessary directories
os.makedirs('faculty_data', exist_ok=True)
os.makedirs('faculty_images', exist_ok=True)


def extract_faculty_info(html_content):
    """Extract faculty information from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')

    faculty_info = {}

    # Name
    name_tag = soup.find('h1')
    faculty_info['name'] = name_tag.text.strip() if name_tag else 'Name not found'

    # Academic title and department
    title_tag = soup.find('h5')
    if title_tag:
        title_text = title_tag.get_text()
        lines = [line.strip() for line in title_text.split('\n') if line.strip()]

        for line in lines:
            if 'Academic Title:' in line:
                faculty_info['academic_title'] = line.replace('Academic Title:', '').strip()
            if 'Dept.' in line:
                faculty_info['department'] = line.strip()
            if 'Date of Joining:' in line:
                faculty_info['joining_date'] = line.replace('Date of Joining:', '').strip()

    # Educational qualifications
    edu_text = title_tag.get_text() if title_tag else ""
    qualifications = []
    faculty_info['qualifications'] = qualifications
    if "Educational Qualification" in edu_text:
        qual_part = edu_text.split('Educational Qualification(s):')[
            1] if 'Educational Qualification(s):' in edu_text else ""
        qualifications = [q.strip() for q in qual_part.split('\n') if q.strip() and not q.strip().startswith('Date of')]
        faculty_info['qualifications'] = qualifications

    # Contact information
    email_tag = soup.find('a', href=lambda h: h and 'mailto:' in h)
    faculty_info['email'] = ""
    if email_tag:
        faculty_info['email'] = email_tag['href'].replace('mailto:', '')

    # Google Scholar URL
    scholar_tag = soup.find('a', href=lambda h: h and 'scholar.google' in h)
    faculty_info['google_scholar'] = ""
    if scholar_tag:
        faculty_info['google_scholar'] = scholar_tag['href']

    # In Brief section - improved extraction
    in_brief = ""
    brief_section = soup.find('h3', string=lambda s: s and 'In Brief' in s)
    if brief_section:
        # Find the parent div with class "cv-item"
        brief_item = brief_section.find_parent('div', class_='cv-item')
        if brief_item:
            # Get the paragraph with class "last"
            brief_p = brief_item.find('p', class_='last')
            if brief_p:
                in_brief = brief_p.text.strip()

    faculty_info['in_brief'] = in_brief

    # Research areas
    research_areas = []
    research_section = soup.find('h3', string=lambda s: s and 'Research Area' in s)
    if research_section:
        # Find the parent div with class "cv-item"
        research_item = research_section.find_parent('div', class_='cv-item')
        if research_item:
            # Get the paragraph with class "last"
            research_p = research_item.find('p', class_='last')
            if research_p:
                # Split by <br> tags
                for item in research_p.stripped_strings:
                    if item.strip():
                        research_areas.append(item.strip())

    faculty_info['research_areas'] = research_areas

    # Subject expertise
    subject_expertise = []
    expertise_section = soup.find('h3', string=lambda s: s and 'Subject Expertise' in s)
    if expertise_section:
        # Find the parent div with class "cv-item"
        expertise_item = expertise_section.find_parent('div', class_='cv-item')
        if expertise_item:
            # Get the paragraph with class "last"
            expertise_p = expertise_item.find('p', class_='last')
            if expertise_p:
                # Extract text with <br> tags preserved
                for item in expertise_p.stripped_strings:
                    if item.strip():
                        subject_expertise.append(item.strip())

    faculty_info['subject_expertise'] = subject_expertise

    # Publications
    publications = []
    pub_table = soup.find('table', class_='table')
    if pub_table:
        rows = pub_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 6:
                publication = {
                    'journal': cells[1].text.strip(),
                    'title': cells[2].text.strip(),
                    'year': cells[3].text.strip(),
                    'role': cells[4].text.strip(),
                    'volume': cells[5].text.strip()
                }
                publications.append(publication)

    faculty_info['publications'] = publications

    # Image URL
    img_tag = soup.find('img', src=lambda s: s and '../educms/upload/faculty/' in s)
    if img_tag:
        faculty_info['image_url'] = img_tag['src']
        # Extract faculty ID from image URL
        if 'faculty/' in img_tag['src']:
            faculty_id = img_tag['src'].split('faculty/')[1]
            faculty_info['faculty_id'] = faculty_id

    return faculty_info


def scrape_faculty_profile(url):
    """Scrape a faculty profile using Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
            page.goto(url, wait_until="networkidle")
            html_content = page.content()
            faculty_info = extract_faculty_info(html_content)
            faculty_info['url'] = url

            # Extract faculty ID from URL
            faculty_id = url.split('?')[1] if '?' in url else 'unknown'
            name = faculty_info['name']
            faculty_info['url_id'] = faculty_id

            # Save the profile image if available
            if 'image_url' in faculty_info:
                img_url = faculty_info['image_url']
                if img_url.startswith('../'):
                    img_url = 'https://www.psgtech.edu/' + img_url[3:]

                # Create directory for images if it doesn't exist
                os.makedirs('faculty_images', exist_ok=True)

                img_path = f"faculty_images/{name}.jpg"

                # Download image
                img_page = context.new_page()
                img_page.goto(img_url, wait_until="networkidle")
                img_page.screenshot(path=img_path)
                img_page.close()

                faculty_info['local_image_path'] = img_path

            return faculty_info

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
        finally:
            browser.close()


def main():
    # Create directories for storing data
    os.makedirs('faculty_data', exist_ok=True)
    os.makedirs('faculty_images', exist_ok=True)

    # Load faculty data from JSON file
    try:
        with open('faculties.json', 'r', encoding='utf-8') as f:
            faculty_data = json.load(f)

        # Extract URLs from the faculty data
        urls = []
        for course in faculty_data:
            for faculty_name, url in faculty_data[course].items():
                urls.append(url)

        print(f"Loaded {len(urls)} faculty URLs from faculties.json")

        # Process each URL
        for url in urls:
            if url is not None:
                # Scrape the faculty profile
                faculty_info = scrape_faculty_profile(url)

                if faculty_info:
                    name = faculty_info['name']
                    # Save the extracted information as JSON
                    with open(f"faculty_data/{name}.json", 'w', encoding='utf-8') as f:
                        json.dump(faculty_info, f, indent=4)

                    print(f"Successfully extracted information for {name}")
                    print(f"Data saved to faculty_data/{name}.json")
                else:
                    print(f"Failed to extract faculty information for {url}")

    except FileNotFoundError:
        print("Error: faculties.json file not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in faculties.json file.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()

