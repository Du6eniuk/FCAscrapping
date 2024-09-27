# This is a file we currently using for the main extraction process
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from datetime import datetime
from datetime import date

# Base URL of the FCA warning list AJAX endpoint
base_url = 'https://www.fca.org.uk/views/ajax'

today = date.today()

# Parameters to filter the results (show 100 items per page and sort by date added)
params = {
    '_wrapper_format': 'drupal_ajax',
    'view_name': 'component_warnings_glossary',
    'view_display_id': 'component_warnings_glossary_block',
    'view_args': '',
    'view_path': '/node/3361',
    'view_base_path': '',
    'view_dom_id': '7efde343ec1eab99611665d0fc81d4bf168f43163e0dfd0f2b2723e84e92aa0c',
    'pager_element': '0',
    'search': '',
    'items_per_page': '100',
    'order': 'field_published_date',
    'sort': 'desc',
    '_drupal_ajax': '1',
    'ajax_page_state[theme]': 'fca',
    'ajax_page_state[theme_token]': '',
    'ajax_page_state[libraries]': 'eJyVk12SpCAMgC-k8rL3oQJGZBsJRULPuKffNG07Vk1Pbe2DEL4E8qtL8Gc3LtIEv-FzcETCUqGYQoXuWAcPRfwKxgHj4G84R6FqY54xi0vkb-YiD9isJ7pF1G0rKUL2aN5BO-MCLcmAn5Jivpm5tgJpOo7DAh6FX_R5mu4RP3jsgS4ezC99L7Ut65ZFQ-jQU9ntGsOa9BOcO9TPLi1nTA78zTJC9atdqG5dHRI5SCPLrr7DCzFD3fuhQEC7IM799nmtIsw2a8S2VLxHatwxk4-Quigrbjixr5QSl_7Ym_q8pf9ja4P0iC45mi9xhCbUjVGez2pvW-9wK6MDtasdf6B75MZmQwGBwEOBCkGnYT078UWmlktzKfKqRS6a4Gmi8vhoot6vMQu4pDOQJcp-4IqvqQpEIeF0Aov5oj2l4egYlGiv2ZgfuNon9BIpW16hYjUnGDuYB95ZcHuOdZ8r09fnb3AFG80t4XAUxxz79HBFHOW7Rj1tmu40axVj4onh_m8joRDeeHmZbajTGH7WU3nkxt_0j-UvqduEQw'
}

# Make the HTTP request with parameters
response = requests.get(base_url, params=params)
response_json = response.json()

# Find the 'insert' command that contains the HTML data
html_content = None
for command in response_json:
    if command.get('command') == 'insert':
        html_content = command.get('data')
        break

if html_content:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Find all relevant data
    dates = soup.find_all('td', class_='views-field-field-published-date')
    links_n_cases = soup.find_all('td', class_='views-field views-field-letter')

    # Debug prints to check the extracted elements
    print(f"Found {len(dates)} dates and {len(links_n_cases)} links.")

    # Extract the data into a list of dictionaries
    extracted_data = []
    for date, link in zip(dates, links_n_cases):
        timestp = date.find('time')['datetime']
        href = link.a['href']
        name = link.a.text.strip()  # Use strip() to remove leading/trailing whitespace
        extracted_data.append({
            'name': name,
            'timestamp': timestp,
            'case_url': f"https://www.fca.org.uk{href}",
            'time_scrapped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Debug print to check the extracted data
    for data in extracted_data:
        print(data)

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(extracted_data)

    # Define the path to save the Excel file
    file_path = f'D:/FuckScam/Scraping/FCA/fca_data/extracted_data_{today}.xlsx'
    directory = os.path.dirname(file_path)

    # Check if the directory exists and create it if it doesn't
    if not os.path.exists(directory):
        os.makedirs(directory)

    # If the file exists, read the existing data and append new data
    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path, engine='openpyxl')
        df = pd.concat([existing_df, df])

    # Drop duplicates based on 'name' and 'case_url'
    df = df.drop_duplicates(subset=['name', 'case_url'])

    # Save the DataFrame to an Excel file
    df.to_excel(file_path, index=False, engine='openpyxl')

    print(f"Data has been saved to '{file_path}'")
else:
    print("No HTML content found in the JSON response.")