import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import json
import re

class WikipediaScraper:
    """A scraper class to fetch data from a web API and Wikipedia."""

    def __init__(self) -> None:
        """
        Initializes the WikipediaScraper with base URLs and endpoints.
        Also starts a session and refreshes the cookie for authentication.

        Attributes:
            base_url: The base URL of the web API.
            country_endpoint: The endpoint to fetch a list of countries.
            leaders_endpoint: The endpoint to fetch leaders' data for a specific country.
            cookies_endpoint: The endpoint to refresh the session cookie.
            leaders_data: A dictionary to store leaders' data keyed by country.
            session: A requests session to handle HTTP requests.

        Methods:
            refresh_cookie: Refreshes the session cookie by making a GET request to the cookie endpoint.
            get_countries: Fetches a list of countries from the API.
            get_leaders: Fetches leaders' data for a given country from the API and stores it in the leaders_data dictionary.
            get_paragraph_containing_names: Fetches the first paragraph from a Wikipedia page that contains the given first and last names.
            to_json_file: Writes the leaders_data dictionary to a JSON file at the specified filepath.
        """
        self.base_url: str = "https://country-leaders.onrender.com"
        self.country_endpoint: str = "/countries"
        self.leaders_endpoint: str = "/leaders"
        self.cookies_endpoint: str = "/cookie"
        self.leaders_data = {}  # Dictionary to hold the fetched leaders' data.
        self.session = requests.Session()  # Start a session for making HTTP requests.
        self.refresh_cookie()  # Refresh the session cookie upon initialization.

    def refresh_cookie(self) -> None:
        """
        Refreshes the session cookie by making a GET request to the cookie endpoint.
        """
        cookie_url: str = f"{self.base_url}{self.cookies_endpoint}" # Construct the full URL for the cookie endpoint.
        try:
            response = self.session.get(cookie_url)  # Attempt to get a new cookie from the API.
            response.raise_for_status()  # Raise an exception if the request was unsuccessful.
        except RequestException as e:
            print(f"An error occurred while refreshing cookie: {e}")  # Handle exceptions such as network errors.

    def get_countries(self):
        """
        Fetches a list of countries from the API.

        Returns:
            A list of countries or None if an error occurs.
        """
        self.refresh_cookie()
        countries_url: str = f"{self.base_url}{self.country_endpoint}"
        try:
            response = self.session.get(countries_url)  # Make the request to the API.
            response.raise_for_status()  # Check for a successful response.
            countries = response.json()  # Parse the JSON response into a list.
            return countries
        except RequestException as e:
            print(f"An error occurred while getting countries: {e}")  # Handle exceptions and return None if an error occurs.
            return None

    def get_leaders(self, country: str) -> None:
        """
        Fetches leaders' data for a given country from the API and stores it in the leaders_data dictionary.

        Args:
            country: The name of the country for which to fetch leaders' data.
        """
        self.refresh_cookie()
        leaders_url: str = f"{self.base_url}{self.leaders_endpoint}"
        try:
            response = self.session.get(leaders_url, params={'country': country})  # Make the request with the country parameter.
            response.raise_for_status()  # Raise HTTPError if the HTTP request returned an unsuccessful status code.
            self.leaders_data[country] = response.json()  # Parse the JSON response and store the result in the leaders_data dictionary under the country key.
        except RequestException as e:
            print(f"An error occurred while getting leaders for {country}: {e}")  # Handle exceptions and store an empty list if an error occurs.
            self.leaders_data[country] = []

    def get_paragraph_containing_names(self, wikipedia_url, first_name, last_name) -> str:
        # Scrape the first paragraph from a Wikipedia page that contains the specified names.
        try:
            # Send a GET request to the Wikipedia page URL.
            response = self.session.get(wikipedia_url)
            # If the response status code indicates a problem (4xx or 5xx), raise an HTTPError exception.
            response.raise_for_status()
            # Use BeautifulSoup to parse the HTML content of the page for data extraction.
            # The 'html.parser' argument specifies the parser to use for parsing the HTML content.
            soup = BeautifulSoup(response.content, 'html.parser')
            # Attempt to find the main content area of the Wikipedia page by ID or class name (inspect page to find the right class name in the source html).
            content = soup.find(id='mw-content-text') or soup.find(class_='rt-commentedText nowrap')
            # If the main content area is found, retrieve all paragraph elements; otherwise, set to an empty list.
            paragraphs = content.find_all('p') if content else []
            # Initialize a variable to hold the first non-empty paragraph text, starting as None.
            first_non_empty_paragraph = None
            # Iterate through each paragraph element found in the main content area.
            for paragraph in paragraphs:
                # Get the text content of the paragraph, stripping leading and trailing whitespace.
                paragraph_text = paragraph.get_text(strip=True)
                # Use a regular expression to remove citation numbers (e.g., "[1]") from the paragraph text.
                clean_text = re.sub(r'\[\d+\]', '', paragraph_text)
                # If we haven't stored a non-empty paragraph yet and the current paragraph has text, store it.
                if not first_non_empty_paragraph and clean_text:
                    first_non_empty_paragraph = clean_text
                # Check if the paragraph contains the first name and, if applicable, the last name.
                # If 'last_name' is None or the string "None", only check for 'first_name'.
                if last_name is None or last_name == "None":
                    if first_name in clean_text:
                        return clean_text
                else:
                    # If both first and last names are provided and present in the paragraph, return it.
                    if first_name in clean_text and last_name in clean_text:
                        return clean_text
            # If no paragraph containing the names is found, return the first non-empty paragraph.
            if first_non_empty_paragraph:
                return first_non_empty_paragraph
            else:
                # If no non-empty paragraphs are found, log a message and return an empty string.
                print(f"No non-empty paragraph found for URL: {wikipedia_url}")
                return ""
        except RequestException as e:
            # If a RequestException occurs (e.g., network issues), log the error and return an empty string.
            print(f"An error occurred while getting paragraphs from Wikipedia: {e}")
            return ""

    def to_json_file(self, filepath) -> None:
        """
        Writes the leaders_data dictionary to a JSON file at the specified filepath.

        Args:
            filepath: The path to the file where the data will be saved.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(self.leaders_data, file, ensure_ascii=False, indent=4)  # Serialize and save the data to the file.
            print(f"Data successfully saved to {filepath}")  # Confirm successful save.
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")  # Handle file I/O exceptions.
