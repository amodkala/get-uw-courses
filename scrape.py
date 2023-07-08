import requests
from bs4 import BeautifulSoup
import json

def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def get_course_details(soup):
    fields = ['course_code', 'course_id', 'course_title', 'course_description', 'metadata']
    center_tags = soup.find_all('center')

    course_details = []
    for center in center_tags:
        div_table = center.find('div', class_='divTable')
        if div_table is not None:
            div_cells = div_table.find_all('div', class_='divTableCell')
            div_cells = [' '.join(cell.text.strip().split()) for cell in div_cells]

            course_code_info = div_cells[0].split()
            div_cells[0] = course_code_info[0] + course_code_info[1]

            course_id = int(div_cells[1].split()[-1])

            metadata_items = div_table.find_all('em')
            metadata = [' '.join(metadata.text.strip().split()) for metadata in metadata_items if metadata.text.strip() != '']

            div_cells = div_cells[:4]
            div_cells.append(metadata)

            course = {field: cell for field, cell in zip(fields, div_cells)}
            course['course_id'] = course_id

            course_details.append(course)

    return course_details

def get_course_info(soup):
    term_info = soup.find('h2').text.strip().split()  # get the first instance of h2 header
    year = int(term_info[1]) % 100
    if term_info[0] == "Fall":
        academic_year = str(year) + str(year + 1)
    else:
        academic_year = str(year - 1) + str(year)

    tables = soup.find_all('table')  # find all tables
    if len(tables) < 2:
        raise ValueError('Less than 2 tables found on the page')
    
    course_subjects = set()
    for row in tables[1].find_all('tr')[1:]:  # skip the header row
        cells = row.find_all('td')
        if len(cells) >= 2:  # check if there are at least 2 cells in the row
            course_subject = cells[0].text.strip()
            # course_number = cells[1].text.strip()
            # course_code = course_subject + course_number  # concatenate the two items
            course_subjects.add(course_subject)
    
    return academic_year, course_subjects

def main():
    index_url = 'https://classes.uwaterloo.ca/uwpcshtm.html'
    index_soup = get_soup(index_url)
    year, course_subjects = get_course_info(index_soup)

    course_details = []
    for course_subject in course_subjects:
        course_url = f'https://ucalendar.uwaterloo.ca/{year}/COURSE/course-{course_subject}.html'
        course_soup = get_soup(course_url)
        details = get_course_details(course_soup)
        for course in details:
            course_details.append(course)

    with open('courses.json', 'w') as f:
        json.dump(course_details, f, indent=4)

if __name__ == '__main__':
    main()

