from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
import pandas as pd
import re
import math
import io
from pywebio.output import put_file

def clean_organization_name(name):
    
    cleaned_name = re.sub(r'\bLtd\.|Inc\.|LLC|Ltd|Pty|PTY|GmbH|PLC|plc|LTD\.|LTD|LIMITED|INC|Inc|Limited|Pvt|PVT|pvt|Pte|S\.p\.a|S\.r\.l\.|S\.r\.L\.|S\.r\.l|S\.p\.A\.|s\. r\. o\.|S\.A\.|S\.L\.|Sp\. z o\.o\.|sp\. z o\.o\.|d\.o\.o\.|S\.r\.l\.|S\.r\.L\.\b', '', str(name), flags=re.IGNORECASE)
    
    cleaned_name = re.sub(r'\([^)]*\)', '', cleaned_name) 
    cleaned_name = re.sub(r'\[.*?\]', '', cleaned_name)   
    cleaned_name = re.sub(r'[©®™¬©,//]', '', cleaned_name)  
    cleaned_name = re.sub(r'[\u0600-\u06FF]+', '', cleaned_name)
    
    
    if ' - ' in cleaned_name:
        cleaned_name = cleaned_name.split(' - ')[0]

    
    cleaned_name = cleaned_name.split('|')[0].strip()

    return cleaned_name

def clean_title(title):
  
    if isinstance(title, float) and math.isnan(title):
        return title, False

    title_mapping = {
        'CTO': 'Chief Technology Officer',
        'Chief Information Officer': 'CIO',
        'Chief Technology Officer': 'Chief Technology Officer',
        'Chief Executive Officer': 'CEO',
        'CEO': 'CEO'
    }

    title_lower = title.lower()
    

    if title_lower in title_mapping:
        return title_mapping[title_lower], False
    
    elif '(cio)' in title_lower or 'cio' in title_lower:
        return 'CIO', False
    
   
    elif 'ceo' in title_lower:
        return 'CEO', False
    
    
    elif 'cto' in title_lower:
        return 'Chief Technology Officer', False
    
    elif 'chief technology officer' in title_lower or 'chief technical officer' in title_lower or 'Chief of Technical Officer and Chief Operating Officer' in title_lower:
        return 'Chief Technology Officer', False
    
   
    elif re.search(r'\bCTO\b', title_lower):
        return 'Chief Technology Officer', False
    
 
    elif '/' in title or '|' in title:
        cleaned_title = re.split(r'\s*[/|]\s*', title)[0]
        return cleaned_title, True
    
     
    elif re.search(r'\b(?:and|,|&)\b', title):
        return title, True
    
  
    elif re.search(r'\([^)]*\)', title):
        cleaned_title = re.sub(r'\([^)]*\)', '', title)
        return cleaned_title, False
    
   
    return title, False

def has_special_characters(row):
    for column in ['Title', 'Organization Name']:
        value = row[column]
        if pd.notna(value) and bool(re.search(r'[^\x00-\x7F]+', str(value))):
            return True
    return False

def app():
   
    csv_file = file_upload("Upload CSV file", accept='.csv')
    df = pd.read_csv(io.BytesIO(csv_file['content']))

    if actions('Clean File', ['Clean']):
       
        df['Title'], df['ChangeFlag'] = zip(*df['Title'].apply(clean_title))

        
        url_pattern = r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

      
        mask = df['Title'].str.contains(url_pattern, na=False)

        
        mask = df.apply(has_special_characters, axis=1)

   
        df = df[~mask]

      
        df[ 'Organization Name'] = df['Organization Name'].apply(clean_organization_name)

      
        df.to_csv("cleaned_file.csv", index=False)

      
        put_text('Cleaning complete! You can now download the cleaned file.')
        put_text('Download cleaned file')

       
        df.to_csv("cleaned_file.csv", index=False)

      
        with open("cleaned_file.csv", "rb") as f:
            content = f.read()
        put_file("cleaned_file.csv", content)

if __name__ == '__main__':
    start_server(app, port=80)
