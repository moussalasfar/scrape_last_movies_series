import requests
from bs4 import BeautifulSoup
import csv
from itertools import zip_longest
import re

def clean_text(text):
    """Remove extra spaces, newlines, and tabs from the text."""
    return re.sub(r'\s+', ' ', text.strip())

def fetch_data(base_url, page_num):
    """Fetch and return data from a given page."""
    url = f"{base_url}?page={page_num}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")

    name_elements = soup.find_all("h3", {"class": "movie-name"})
    rating_elements = soup.find_all("div", {"class": "is-rated"})
    info_elements = soup.find_all("div", {"class": "info-split"})
    link_elements = soup.find_all("a", {"class": "movie-link"})

    names = [element.text.strip() for element in name_elements]
    ratings = [element.text.strip() for element in rating_elements]
    infos = [element.text.strip() for element in info_elements]
    links = ["https://goku.sx" + element['href'].strip() for element in link_elements]

    return names, ratings, infos, links

def fetch_additional_data(links):
    """Fetch and return additional data (description, genre, country, time) from individual pages."""
    descriptions = []
    genres = []
    countries = []
    times = []

    for link in links:
        response = requests.get(link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        description_element = soup.find("div", {"class": "text-cut"})
        descriptions.append(clean_text(description_element.text) if description_element else 'N/A')

        value_elements = soup.find_all("div", {"class": "value"})
        if value_elements:
            genres.append(clean_text(value_elements[0].text))
            countries.append(clean_text(value_elements[3].text))
            if len(value_elements) > 4:
                times.append(clean_text(value_elements[4].text))
            else:
                times.append('N/A')
        else:
            genres.append('N/A')
            countries.append('N/A')
            times.append('N/A')

    return descriptions, genres, countries, times

def scrape_movies(max_pages=6):
    """Scrape movie data from multiple pages."""
    movie_names, ratings, infos, links = [], [], [], []
    dates, times = [], []

    for page_num in range(max_pages + 1):
        names, rates, page_infos, page_links = fetch_data("https://goku.sx/movies", page_num)
        movie_names.extend(names)
        ratings.extend(rates)
        infos.extend(page_infos)
        links.extend(page_links)

        dates.extend([info.split('\n\n')[0].strip() for info in page_infos])
        times.extend([info.split('\n\n')[1].strip() for info in page_infos])
        print(f"Movies Page {page_num} processed")

    descriptions, genres, countries, _ = fetch_additional_data(links)
    return movie_names, genres, ratings, descriptions, countries, dates, times, links

def scrape_series(max_pages=2):
    """Scrape series data from multiple pages."""
    serie_names, ratings, infos, links = [], [], [], []
    episodes = []

    for page_num in range(max_pages + 1):
        names, rates, page_infos, page_links = fetch_data("https://goku.sx/tv-series", page_num)
        serie_names.extend(names)
        ratings.extend(rates)
        infos.extend(page_infos)
        links.extend(page_links)

        episodes.extend([info.split('\n')[1].strip() for info in page_infos])
        print(f"Series Page {page_num} processed")

    descriptions, genres, countries, times = fetch_additional_data(links)
    return serie_names, episodes, genres, ratings, descriptions, countries, times, links

def write_to_csv(file_path, headers, data):
    """Write data to CSV file."""
    with open(file_path, "w", newline='', encoding='utf-8') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(headers)
        wr.writerows(data)
    print(f"Data successfully written to {file_path}")

# Scrape movies and write to CSV
movie_data = scrape_movies()
movie_file_list = list(zip_longest(*movie_data, fillvalue=''))
write_to_csv("last_movies.csv",
             ["movie_name", "category", "movie_rate", "description", "country", "date", "duration", "movie_link"],
             movie_file_list)

# Scrape series and write to CSV
serie_data = scrape_series()
serie_file_list = list(zip_longest(*serie_data, fillvalue=''))
write_to_csv("last_series.csv",
             ["serie_name", "season_episode", "category", "serie_rate", "description", "country", "duration", "movie_link"],
             serie_file_list)
