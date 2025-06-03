# Pokémon Web Scraper  Pokédex

![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Optional: Add a license file -->

A Python script to scrape comprehensive Pokémon data from [pokemondb.net](https://pokemondb.net/pokedex/all) and save it into a structured CSV file.

## 📋 Table of Contents

- [Features](#-features)
- [Technologies Used](#-technologies-used)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Output](#-output)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

## ✨ Features

-   Scrapes data for all Pokémon listed on the target website.
-   Extracts key information:
    -   National Pokédex Number
    -   Name
    -   Type(s)
    -   Total Base Stats
    -   HP
    -   Attack
    -   Defense
    -   Special Attack (Sp. Atk)
    -   Special Defense (Sp. Def)
    -   Speed
-   Saves the collected data into a clean, ready-to-use CSV file (`pokemon_data.csv`).
-   Handles Pokémon with single or dual types.

## 🛠️ Technologies Used

-   **Python 3**: Core programming language.
-   **Requests**: For making HTTP requests to the website.
-   **Beautiful Soup 4 (bs4)**: For parsing HTML content.
-   **Pandas**: For data manipulation and saving to CSV.

## ⚙️ Prerequisites

-   Python 3.7 or higher.
-   `pip` (Python package installer).

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Theotime66/Web_Scrapper_Pokemon.git
    cd Web_Scrapper_Pokemon
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Usage

Once the installation is complete, you can run the scraper script from the project's root directory:

```bash
python main.py
```

The script will then:
1.  Fetch the webpage containing the Pokémon list.
2.  Parse the HTML to extract data for each Pokémon.
3.  Print a confirmation message to the console upon completion.
4.  Generate a `pokemon_data.csv` file in the same directory with the scraped data.

## 📊 Output

The script generates a CSV file named `pokemon_data.csv` with the following columns:

-   `#`: National Pokédex number.
-   `Name`: Name of the Pokémon.
-   `Type 1`: Primary type of the Pokémon.
-   `Type 2`: Secondary type of the Pokémon (can be empty if the Pokémon has only one type).
-   `Total`: Sum of all base stats.
-   `HP`: Hit Points.
-   `Attack`: Attack stat.
-   `Defense`: Defense stat.
-   `Sp. Atk`: Special Attack stat.
-   `Sp. Def`: Special Defense stat.
-   `Speed`: Speed stat.

Example `pokemon_data.csv` structure:

```csv
#,Name,Type 1,Type 2,Total,HP,Attack,Defense,Sp. Atk,Sp. Def,Speed
001,Bulbasaur,Grass,Poison,318,45,49,49,65,65,45
002,Ivysaur,Grass,Poison,405,60,62,63,80,80,60
...
```
