# Used for manipulation and pulling links

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import date

today = date.today()

# Function to get URLs after "Website:"
def get_url(link):
    url = link
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    address_element = soup.find("strong", string=re.compile(r"Website:", re.I))
    if address_element:
        next_sibling = address_element.next_sibling
        if next_sibling:
            website_text = next_sibling.strip()
            return website_text
    return None

# Function to extract links from the 'name' column as a backup
def extract_links_from_name(name):
    urls = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(?:\.[a-zA-Z]{2,6})?\b', name)
    return ', '.join(urls) if urls else None

# Function to extract notes from the 'name' column
def extract_notes(name):
    match = re.search(r'\(([^)]+)\)', name, re.IGNORECASE)
    if match and 'clone' in match.group(1).lower():
        return match.group(1)
    return ""

# Function to extract date from 'timestamp'
def extract_date(timestamp):
    return timestamp.split("T")[0]

# Function to extract date from 'time_scrapped'
def extract_scrapped_date(time_scrapped):
    return time_scrapped.split(" ")[0]

# Function to clean names
def clean_name(name):
    # Remove any text inside parentheses
    name = re.sub(r'\s*\(.*?\)\s*', '', name)
    # Keep only the part before the first slash
    name = name.split('/')[0].strip()
    return name

# Load new data from 'extracted_data.xlsx'
extracted_file_path = f'D:/FuckScam/Scraping/FCA/fca_data/extracted_data_{today}.xlsx'
df_new = pd.read_excel(extracted_file_path)

# Check if 'updated_data.xlsx' exists and load existing data
updated_file_path = f'D:/FuckScam/Scraping/FCA/fca_data/updated_data_{today}.xlsx'
if os.path.exists(updated_file_path):
    df_existing = pd.read_excel(updated_file_path)
    # Identify new entries
    df_new_entries = df_new[~df_new[['name', 'case_url']].apply(tuple, axis=1).isin(df_existing[['name', 'case_url']].apply(tuple, axis=1))]
else:
    df_new_entries = df_new

# Add 'notes' column
df_new_entries['notes'] = df_new_entries['name'].apply(extract_notes)

# Replace 'timestamp' and 'time_scrapped' with dates
df_new_entries['timestamp'] = df_new_entries['timestamp'].apply(extract_date)
df_new_entries['time_scrapped'] = df_new_entries['time_scrapped'].apply(extract_scrapped_date)

# Add 'links' column by applying get_url function to 'case_url' column for new entries
df_new_entries['links'] = df_new_entries['case_url'].apply(get_url)

# Fill missing links with links extracted from 'name' column for new entries
df_new_entries['links'] = df_new_entries.apply(lambda row: row['links'] if row['links'] else extract_links_from_name(row['name']), axis=1)

# Clean the 'name' column
df_new_entries['name'] = df_new_entries['name'].apply(clean_name)

# Append new entries to the existing data
if os.path.exists(updated_file_path):
    df_combined = pd.concat([df_existing, df_new_entries], ignore_index=True)
else:
    df_combined = df_new_entries

# Add new columns with empty values
df_combined['Country'] = ''
df_combined['Cleaning'] = ''
df_combined['Source'] = 'FCA'

# Rename columns
df_combined.rename(columns={
    'name': 'Name',
    'timestamp': 'Date added to website',
    'case_url': 'CASE',
    'time_scrapped': 'Date Added',
    'notes': 'Notes',
    'links': 'PULLED LINKS'
}, inplace=True)

# Reorder columns
df_combined = df_combined[['Date Added', 'Country', 'Source', 'Name', 'PULLED LINKS', 'Cleaning' , 'Notes', 'Date added to website', 'CASE']]

# Save the updated DataFrame to 'updated_data.xlsx'
df_combined.to_excel(updated_file_path, index=False, engine='openpyxl')

print(f"Updated data has been saved to '{updated_file_path}'")