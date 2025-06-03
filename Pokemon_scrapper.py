#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Converted from Pokemon scrapper.ipynb

# # Pokemon Scrapper

# A project to learn web scrapping

# ## Imports and test requesting the page

import requests

URL = "https://pokemondb.net/pokedex/national"

# Send a GET request to the URL
response = requests.get(URL)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print("Successfully fetched the page!")
    # The HTML content of the page
    html_content = response.text
    # print(html_content[:500]) # Print first 500 characters to see
else:
    print(f"Failed to fetch page. Status code: {response.status_code}")
    exit() # Exit if we couldn't get the page

# ## Scrapping of the page

# ### Imports and Setup

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re # For regular expressions
from urllib.parse import urljoin # For constructing absolute URLs

BASE_URL = "https://pokemondb.net"
NATIONAL_DEX_URL = f"{BASE_URL}/pokedex/national"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
# Be a good web citizen!
REQUEST_DELAY_SECONDS = 0.01 # Delay between requests to detail pages

# ### Function to get all Pokémon detail page URLs and their Generations

def get_pokemon_detail_links(listing_url):
    """
    Fetches the main Pokedex listing page and extracts links to individual Pokemon
    detail pages along with their generation.
    Returns a list of dictionaries: [{'url': '...', 'generation': '...'}, ...]
    """
    pokemon_info_list = []
    print(f"Fetching listing page: {listing_url}")
    try:
        response = requests.get(listing_url, headers=HEADERS, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching listing page {listing_url}: {e}")
        return pokemon_info_list

    soup = BeautifulSoup(response.text, 'html.parser')
    
    main_content = soup.find('main', id='main')
    if not main_content:
        print("Warning: Could not find <main id='main'> element. Aborting link extraction.")
        return pokemon_info_list

    # Find all generation headers (e.g., <h2 id="gen-1">Generation 1 Pokémon</h2>)
    generation_headers = main_content.find_all('h2', id=re.compile(r'^gen-\d+'))
    
    processed_urls = set() # To keep track of URLs already added

    for header in generation_headers:
        generation_text = header.text.strip().replace(" Pokémon", "") # Gets "Generation X"
        print(f"Processing {generation_text}...")
        
        # The Pokémon for this generation are typically in a div immediately following the h2,
        # or the next div with class 'infocard-list'
        current_element = header.find_next_sibling()
        infocard_container = None
        
        while current_element:
            if current_element.name == 'div' and ('infocard-list' in current_element.get('class', []) or 'infocard-grid' in current_element.get('class', [])):
                infocard_container = current_element
                break
            if current_element.name == 'h2' and current_element.get('id','').startswith('gen-'): # Stop if we hit the next gen header
                break
            current_element = current_element.find_next_sibling()

        if not infocard_container:
            print(f"  Warning: Could not find infocard container for {generation_text}")
            continue

        infocards = infocard_container.find_all('div', class_='infocard')
        print(f"  Found {len(infocards)} infocards for {generation_text}.")

        for card in infocards:
            link_tag = card.select_one('span.infocard-lg-img a[href^="/pokedex/"], span.infocard-sm-img a[href^="/pokedex/"]')
            if not link_tag:
                link_tag = card.find('a', class_='ent-name', href=re.compile(r'^/pokedex/'))

            if link_tag and link_tag.has_attr('href'):
                relative_url = link_tag['href']
                if re.match(r'/pokedex/[a-zA-Z0-9-]+(?:/(?!sprites|other-forms|national).*)*$', relative_url): # More specific to avoid non-detail pages
                    absolute_url = urljoin(BASE_URL, relative_url)
                    if absolute_url not in processed_urls:
                        pokemon_info_list.append({'url': absolute_url, 'generation': generation_text})
                        processed_urls.add(absolute_url)
            # else:
            #     print(f"    Warning: Could not find a valid Pokémon link in an infocard for {generation_text}.")
            #     print(f"    Card HTML (first 100 chars): {str(card)[:100]}")


    print(f"\nExtracted info for {len(pokemon_info_list)} unique Pokémon from the listing page.")
    return pokemon_info_list

# ### Function to scrape data from a single Pokémon detail page (Corrected version)

def scrape_pokemon_detail_page(pokemon_entry_from_list): # pokemon_entry_from_list is the dict
    """
    Fetches a Pokemon detail page and scrapes specific information.
    pokemon_entry_from_list is a dict like {'url': '...', 'generation': '...'}
    """
    # ---- START OF CRITICAL SECTION ----
    actual_url_to_fetch = pokemon_entry_from_list['url']  # Make sure you extract the URL string
    current_generation = pokemon_entry_from_list['generation'] # And the generation string
    
    # This print statement should now correctly show the generation and the URL string
    print(f"Scraping {current_generation} detail page: {actual_url_to_fetch}") 
    
    pokemon_data = {'url': actual_url_to_fetch, 'generation': current_generation, 'name': "N/A"}
    
    try:
        # Ensure requests.get() is called with the URL STRING
        response = requests.get(actual_url_to_fetch, headers=HEADERS, timeout=20) 
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # This error print should also use the actual URL string
        print(f"  Error fetching detail page {actual_url_to_fetch}: {e}") 
        return pokemon_data 
    # ---- END OF CRITICAL SECTION ----

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- Name ---
    name_element = soup.find('h1')
    pokemon_data['name'] = name_element.text.strip() if name_element else "N/A" 

    # --- Vitals Table (Type, Height, Weight, Abilities) ---
    vitals_tables = soup.find_all('table', class_='vitals-table')
    
    pokemon_data['types'] = "N/A"
    pokemon_data['weight_kg'] = None
    pokemon_data['height_m'] = None
    pokemon_data['abilities'] = "N/A"
    pokemon_data['hidden_abilities'] = "N/A"

    if not vitals_tables:
        print(f"  Warning: Could not find vitals table on {actual_url_to_fetch} for {pokemon_data.get('name')}")
    else:
        main_vitals_table = vitals_tables[0] 

        types_list = []
        type_elements = main_vitals_table.select('th:-soup-contains("Type") + td a.type-icon')
        for t_elem in type_elements:
            types_list.append(t_elem.text.strip())
        pokemon_data['types'] = ", ".join(types_list) if types_list else "N/A"
        
        for row in main_vitals_table.find_all('tr'):
            header_tag = row.find('th')
            if header_tag:
                header_text = header_tag.text.strip()
                value_tag = row.find('td')
                if value_tag:
                    value_text = value_tag.text.strip()
                    if header_text == "Weight":
                        match = re.search(r'([\d\.]+)\s*kg', value_text)
                        if match:
                            pokemon_data['weight_kg'] = float(match.group(1))
                    elif header_text == "Height":
                        match = re.search(r'([\d\.]+)\s*m', value_text)
                        if match:
                            pokemon_data['height_m'] = float(match.group(1))
        
        abilities_list = []
        hidden_abilities_list = []
        abilities_th = main_vitals_table.find(lambda tag: tag.name == 'th' and "Abilities" in tag.text)
        if abilities_th:
            abilities_td = abilities_th.find_next_sibling('td')
            if abilities_td:
                current_abilities_group = abilities_list 
                for tag_group in abilities_td.contents: 
                    if isinstance(tag_group, str) and tag_group.strip() == "": 
                        continue
                    if hasattr(tag_group, 'name') and tag_group.name == 'br': 
                        continue
                    if hasattr(tag_group, 'name') and tag_group.name == 'small' and 'hidden ability' in tag_group.text.lower():
                        current_abilities_group = hidden_abilities_list
                        continue 
                    if hasattr(tag_group, 'name') and tag_group.name in ['a', 'span']:
                        ability_name = tag_group.text.strip()
                        if ability_name: 
                            if 'hidden ability' in tag_group.get('title', '').lower() or \
                               (tag_group.find_next_sibling('small') and 'hidden ability' in tag_group.find_next_sibling('small').text.lower()):
                                if ability_name not in hidden_abilities_list:
                                    hidden_abilities_list.append(ability_name)
                            elif ability_name not in abilities_list and ability_name not in hidden_abilities_list: 
                                abilities_list.append(ability_name)
                    elif isinstance(tag_group, str) and tag_group.strip():
                        ability_name = tag_group.strip()
                        if ability_name and ability_name not in abilities_list and ability_name not in hidden_abilities_list:
                             abilities_list.append(ability_name)
        pokemon_data['abilities'] = ", ".join(list(dict.fromkeys(abilities_list))) if abilities_list else "N/A"
        pokemon_data['hidden_abilities'] = ", ".join(list(dict.fromkeys(hidden_abilities_list))) if hidden_abilities_list else "N/A"

    stat_names = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
    for stat in stat_names:
        pokemon_data[stat.replace('. ', '_').replace(' ', '_')] = None 

    stats_table = None
    for table_idx, table in enumerate(vitals_tables):
        th_texts = [th.text.strip() for th in table.select('tr > th')]
        if any(stat_name in th_texts for stat_name in ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]):
            if table.find(lambda tag: tag.name == 'th' and "Total" in tag.text.strip()):
                stats_table = table
                break
            if not stats_table and table_idx > 0 : 
                 stats_table = table 
    if stats_table:
        for row in stats_table.find_all('tr'):
            th = row.find('th')
            if th:
                stat_name_raw = th.text.strip()
                stat_name_key = stat_name_raw.replace('.', '') 
                if stat_name_key in stat_names or stat_name_raw in stat_names:
                    stat_value_td = row.find('td', class_='cell-num') 
                    if not stat_value_td: 
                        stat_value_td = row.find_all('td')[-1] 
                    if stat_value_td:
                        try:
                            df_col_name = stat_name_raw.replace('. ', '_').replace(' ', '_')
                            pokemon_data[df_col_name] = int(stat_value_td.text.strip())
                        except (ValueError, IndexError):
                            print(f"  Warning: Could not parse stat value for {stat_name_raw} for {pokemon_data['name']}")
                            pokemon_data[df_col_name] = None
    else:
        print(f"  Warning: Could not find stats table for {pokemon_data.get('name')} on {actual_url_to_fetch}")

    print(f"  Successfully scraped: {pokemon_data.get('name', 'Unknown Pokemon')} ({pokemon_data.get('generation')})")
    return pokemon_data

# ### Main Execution Logic

if __name__ == "__main__": # For notebook execution, this part runs directly
    
    print("--- Starting Pokémon Scraping ---")
    
    # 1. Get all Pokémon detail page URLs and their generations
    pokemon_entries = get_pokemon_detail_links(NATIONAL_DEX_URL)
    
    # For testing, you might want to limit the number of pages:
    # pokemon_entries = pokemon_entries[:20] # Scrape only the first 20 Pokémon to test

    all_pokemon_data = []

    if pokemon_entries:
        print(f"\nStarting to scrape {len(pokemon_entries)} Pokémon detail pages...\n")
        
        for i, entry in enumerate(pokemon_entries): # entry is {'url': '...', 'generation': '...'}
            print(f"--- Processing Pokémon {i+1}/{len(pokemon_entries)} ---")
            data = scrape_pokemon_detail_page(entry) 
            if data:
                all_pokemon_data.append(data) # 'data' here definitely contains 'generation'
            
            time.sleep(REQUEST_DELAY_SECONDS) 
        
        print("\n--- SCRAPING COMPLETE ---")
        
        if all_pokemon_data:
            # At this point, all_pokemon_data is a list of dicts, and each dict should have a 'generation' key.
            df = pd.DataFrame(all_pokemon_data)
            
            # You can verify if 'generation' column exists here before reindexing:
            # print("\nColumns in DataFrame before reordering:", df.columns.tolist())
            # print(df[['name', 'generation']].head()) # Check if generation column has data

            stat_cols = ['HP', 'Attack', 'Defense', 'Sp_Atk', 'Sp_Def', 'Speed']
            
            # !!! CRITICAL LINE: Ensure 'generation' is in this list EXACTLY as 'generation' !!!
            ordered_cols = ['name', 'generation', 'types', 'weight_kg', 'height_m', 
                           'abilities', 'hidden_abilities'] + stat_cols + ['url']
            
            # This reindex operation uses the ordered_cols list. If 'generation' isn't in it, it gets dropped.
            df = df.reindex(columns=ordered_cols)

            # You can verify columns again after reindexing:
            # print("\nColumns in DataFrame AFTER reordering:", df.columns.tolist())
            # print(df[['name', 'generation']].head()) # Check again

            csv_filename = 'pokemon_pokedex_data_with_generations.csv'
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"\nData for {len(all_pokemon_data)} Pokémon saved to {csv_filename}")
            
            print("\nFirst 5 entries from CSV (will be read back to verify):")
            try:
                df_read_test = pd.read_csv(csv_filename)
                print(df_read_test.head())
                if 'generation' not in df_read_test.columns:
                    print("WARNING: 'generation' column is NOT in the saved CSV file according to read_csv.")
                else:
                    print("'generation' column IS in the saved CSV file.")
            except Exception as e:
                print(f"Error reading back CSV for verification: {e}")
            
        else:
            print("No data was scraped.")
            
    else:
        print("No detail links found from the main Pokedex page. Exiting.")

# ## Data visualisation / analysis (not needed for scrapping)

import pandas as pd

# data = pd.read_csv('pokemon_pokedex_data_with_generations.csv') # Renamed to avoid conflict
# print(data.head())
# Note: The above lines are commented out to prevent re-reading the CSV immediately
# if the script is run, as the main part of the script already creates and prints from it.
# If you want to run this analysis part independently later, uncomment them and ensure
# the CSV file exists.

# Example of how you might use the data if it were loaded into a DataFrame named `df_analysis`:
# Assuming `df` from the main scraping block is still in scope if run in an interactive Python session
# or if this code is moved into the `if __name__ == "__main__":` block after CSV creation.

# For direct execution of this cell's original intent IF df is available:
# Check if df exists from the scraping part, otherwise try to load
if 'df' in locals() or 'df' in globals():
    df_analysis = df 
    print("\n--- Analyzing data from scraping session ---")
elif pd.io.common.file_exists('pokemon_pokedex_data_with_generations.csv'):
    print("\n--- Loading data from CSV for analysis ---")
    df_analysis = pd.read_csv('pokemon_pokedex_data_with_generations.csv')
else:
    df_analysis = None
    print("\n--- No data available for analysis ---")

if df_analysis is not None:
    print("Top 5 rows of the dataset for analysis:")
    print(df_analysis.head())

    print('\nWeights:')
    # data['weight_kg'].describe() # Original notebook line referred to 'data'
    print(df_analysis['weight_kg'].describe())


    # Find the name of the Pokémon with the highest weight
    # Only keep the generation 1
    # data_generation = data[data['generation'] == 'Generation 3'] # Original
    data_generation_3 = df_analysis[df_analysis['generation'] == 'Generation 3']
    
    if not data_generation_3.empty:
        max_weight_gen3 = data_generation_3['weight_kg'].max()
        # .values[0] might fail if multiple Pokémon have the same max weight or if Series is empty
        max_weight_pokemon_gen3 = data_generation_3[data_generation_3['weight_kg'] == max_weight_gen3]['name']
        if not max_weight_pokemon_gen3.empty:
            print(f"The Pokémon in Generation 3 with the highest weight is: {max_weight_pokemon_gen3.iloc[0]} with a weight of {max_weight_gen3} kg")
        else:
            print("Could not find Pokémon with max weight in Generation 3 (or data missing).")

        #print('Heights:')
        #data['height_m'].describe() # Original
        
        max_height_gen3 = data_generation_3['height_m'].max()
        max_height_pokemon_gen3 = data_generation_3[data_generation_3['height_m'] == max_height_gen3]['name']
        if not max_height_pokemon_gen3.empty:
            print(f"The Pokémon in Generation 3 with the highest height is: {max_height_pokemon_gen3.iloc[0]} with a height of {max_height_gen3} m")
        else:
            print("Could not find Pokémon with max height in Generation 3 (or data missing).")
    else:
        print("No Generation 3 data found for weight/height analysis.")
else:
    print("Skipping analysis as DataFrame could not be loaded/found.")