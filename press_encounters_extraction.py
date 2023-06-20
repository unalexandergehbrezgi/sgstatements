import pandas as pd
import sys
import requests
from bs4 import BeautifulSoup
import numpy as np
import re
from datetime import datetime
import os

########################################################################################################################
########################################################################################################################
################################################### INPUT VARIABLES ####################################################
########################################################################################################################
########################################################################################################################

# UN latest SG statemens
base_url = 'https://www.un.org/sg/en/content/sg/press-encounters'

########################################################################################################################
########################################################################################################################
################################################## FUNCTIONS ###########################################################
########################################################################################################################
########################################################################################################################

def get_total_page_number (base_url):

    total_page_number  = 17

    return(total_page_number)

def get_statements_url (base_url, page_number):

    urls = {}

    statement_url = f'{base_url}?page={page_number}'

    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'  # This is another valid field
    }

    # Extract document IDs from the search results
    response = requests.get(statement_url, headers=headers)

    # Check that the response was successful
    if response.status_code == 200:
        pass
    else:
        return (sys.exit(response))

    soup = BeautifulSoup(response.text, "html.parser")
    pagebody = soup.find('div', class_='main-container container')
    container = pagebody.find('div', class_='row body-container')
    content = container.find('div', class_='view-content')
    # Find all elements with a class attribute
    elements = content.find_all('div', class_=True, recursive=False)

    for c in elements:
        cl = c['class'][0]

        if cl != 'date-display-single':
            # get city
            city_element = c.find('span', class_='views-field-field-city-location')
            city = city_element.find('span', class_='field-content').text

            # get url
            link_element = c.find('a')
            url = link_element['href']

            urls[url] = city

    return(urls)

def get_statements (base_url):

    statement_url = f'https://www.un.org/{base_url}'

    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'  # This is another valid field
    }

    # Extract document IDs from the search results
    response = requests.get(statement_url, headers=headers)

    # Check that the response was successful
    if response.status_code == 200:
        pass
    else:
        return (sys.exit(response))

    soup = BeautifulSoup(response.text, "html.parser")
    pagebody = soup.find('div', class_='main-container container')
    container = pagebody.find('div', class_='row body-container')
    content = container.find('section', class_='region region-content')

    # Get Date
    date_element = content.find('h4', class_='date-display-single')
    date = date_element.find('span', class_='date-display-single').text.strip()

    # Get Header
    header = content.find('h2').text.strip()

    # get body
    text_content = content.find('div', class_='content')
    field_items = text_content.find('div', class_='field-items')
    p_elements = field_items.find_all('p')

    all_text = ''
    for p in p_elements:
        text = p.get_text(strip=True)
        text = text.strip("'")
        all_text = all_text + text + " "

    return(date, header, all_text, statement_url)

def split_content(text, max_length):
    # Split the text into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def date_format (date):

    # Convert the date string to a datetime object
    date_object = datetime.strptime(date, '%d %B %Y')

    # Format the datetime object as a string in the desired format
    formatted_date = date_object.strftime('%Y-%B-%d')

    return(formatted_date)

def modify_filename(filename, filenames):
    filename = filename.replace('/', '_')
    base_name, extension = os.path.splitext(filename)
    counter = 0
    modified_filename = f'{filename}_0'


    while modified_filename in filenames:
        counter += 1
        modified_filename = f"{base_name}_{counter}{extension}"

    return modified_filename

path_to_save = r'C:/Users/alexa/OneDrive/Dokumente/Arbeit/Arbeitgeber/United Nations/Work/press_encounters'

filenames= []

total_page_number = get_total_page_number(base_url)

for page_number in range(total_page_number):
    print(page_number)
    page_urls = get_statements_url (base_url, page_number)

    for url in page_urls:
        place = page_urls[url]
        date, title, content, statement_url = get_statements(url)

        # format date
        formatted_date = date_format(date)

        # sourcefile
        filename = f'{formatted_date}_Press_Encounters_{place}'
        modified_filename = modify_filename(filename, filenames)
        filenames.append(modified_filename)

        # split content
        content_chunks = split_content(content, 1000)

        # sourcepage
        for i in range(len(content_chunks)):
            sourcepage = f'{modified_filename}_{i}'

            # Create a DataFrame with existing columns
            data = {
                'id': [sourcepage],
                'content': [str(place + '|' + date + '|' + title + '|' + content_chunks[i])],
                'sourcepage': [sourcepage],
                'sourcefile': [modified_filename],
                'url': [statement_url]
            }

            df = pd.DataFrame(data)

            file_path = f'{path_to_save}/{sourcepage}.json'

            # Save DataFrame as JSON
            df.to_json(file_path, orient='records')

        print(modified_filename)


