import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import json
import re
from opentelemetry import trace

tracer = trace.get_tracer("mytracer")


class WikipediaScraper:
    """
    A scraper class for fetching and processing data from Wikipedia and a specific API for country leaders.
    Attributes:
        base_url (str): The base URL for the API to fetch leaders' data.
        leaders_endpoint (str): The endpoint at the API for fetching leaders.
        cookies_endpoint (str): The endpoint at the API for refreshing cookies.
        cookie (RequestsCookieJar): Cookies returned by the API for session management.
        leaders_data (dict): A dictionary to store leaders' data keyed by country.
    """
    def __init__(self):
        """
        Initializes the WikipediaScraper with default values.
        """
        self.base_url = "https://country-leaders.onrender.com"
        self.country_endpoint = "/countries"
        self.leaders_endpoint = "/leaders"
        self.cookies_endpoint = "/cookie"
        self.leaders_data = {}  # Initialize an empty dictionary to store leaders' data keyed by country.
        self.cookie = None  # Initialize the cookie attribute to None.

    def refresh_cookie(self):
        """
        Refreshes the session cookie required for making requests to the API.
        """
        cookie_url = f"{self.base_url}{self.cookies_endpoint}" # Construct the full URL for the cookie endpoint.
        try:
            response = requests.get(cookie_url)  # Make a GET https request to the cookie endpoint to obtain a new cookie.
            response.raise_for_status()  # # Check if the request was successful (status code 200). Will raise an HTTPError if the request returned an unsuccessful status code
            self.cookie = response.cookies  # Update the cookie attribute with the new cookie from the response.
        except RequestException as e:
            print(f"An error occurred while refreshing cookie: {e}") # Print an error message if an exception occurs (e.g., network problem, invalid URL).
            self.cookie = None # This refreshes the cookie
        pass

    @tracer.start_as_current_span("get_countries")
    def get_countries(self):
        """
        Fetches a list of countries from the API.
        This method constructs a URL by appending the country endpoint to the base URL,
        then makes a GET request to that URL. If the request is successful, it parses
        the response as JSON and returns the resulting list. If any request-related
        error occurs, it prints an error message and returns None.

        Returns:
            list: A list of countries if the request is successful, None otherwise.
        """
        # Construct the full URL for fetching countries by appending the country endpoint to the base URL
        countries_url = f"{self.base_url}{self.country_endpoint}"
        try:
            # Make a GET request to the constructed URL, passing the stored cookie for authentication
            response = requests.get(countries_url, cookies=self.cookie)
            # Raise an exception if the request was unsuccessful (e.g., network error, 404 not found, etc.)
            response.raise_for_status()
            # Parse the response content as JSON, which is expected to be a list of countries
            countries = response.json()
            # Return the list of countries
            return countries
        except RequestException as e:
            # If a request exception occurs, print an error message with the exception details
            print(f"An error occurred while getting countries: {e}")
            # Return None to indicate that the request was unsuccessful
            return None
        # The 'pass' statement is unnecessary here and can be removed

    @tracer.start_as_current_span("get_leaders")
    def get_leaders(self, country):
        """
        Fetches leaders for a given country from the API and stores their data.
        This method constructs a URL for fetching leaders, checks if the cookie is set,
        and if not, refreshes it. It then makes a GET request with the country as a parameter.
        If the request is successful, it updates the leaders_data dictionary with the response.
        If a 403 error occurs, indicating an expired or invalid cookie, it refreshes the cookie
        and retries the request. If any other request-related error occurs, it logs the error
        and sets the country's leaders data to an empty list.

        Args:
            country (str): The country for which to fetch leaders.

        Updates:
            self.leaders_data: Updates the dictionary with the leaders' data for the given country.
        """
        # Construct the full URL for fetching leaders by appending the leaders endpoint to the base URL
        leaders_url = f"{self.base_url}{self.leaders_endpoint}"
        # Check if the cookie is set, if not, call the method to refresh it
        if not self.cookie:
            self.refresh_cookie()
        try:
            # Make a GET request to the constructed URL, passing the stored cookie and the country as a parameter
            response = requests.get(leaders_url, cookies=self.cookie, params={'country': country})
            # Raise an exception if the request was unsuccessful
            response.raise_for_status()
            # Parse the response content as JSON and update the leaders_data dictionary with the data for the given country
            self.leaders_data[country] = response.json()
        except requests.exceptions.HTTPError as e:
            # If a 403 HTTP error occurs, it indicates that the cookie has expired or is invalid
            if e.response.status_code == 403:
                # Inform the user that the cookie is being refreshed
                print("Cookie expired or invalid, refreshing cookie and retrying...")
                # Refresh the cookie
                self.refresh_cookie()
                # Retry the GET request with the new cookie
                response = requests.get(leaders_url, cookies=self.cookie, params={'country': country})
                # If the retry is successful, update the leaders_data dictionary
                if response.status_code == 200:
                    self.leaders_data[country] = response.json()
                else:
                    # If the retry is unsuccessful, log the failure and set the country's leaders data to an empty list
                    print(f"Failed to get leaders after refreshing cookie: {response.status_code}")
                    self.leaders_data[country] = []
        except RequestException as e:
            # If any other request exception occurs, log the error and set the country's leaders data to an empty list
            print(f"An error occurred while getting leaders for {country}: {e}")
            self.leaders_data[country] = []
        # The 'pass' statement is unnecessary here and can be removed

    @tracer.start_as_current_span("get_paragraph_containing_names")
    def get_paragraph_containing_names(self, wikipedia_url, first_name, last_name):
        """
        Fetches and returns the first paragraph that contains both the first name and the last name from a Wikipedia page.
        This method makes a GET request to the provided Wikipedia URL, parses the response content using BeautifulSoup
        to find all paragraphs, and returns the text of the first paragraph that contains both the first name and the last name.
        If the request fails or no such paragraph is found, it logs an error and returns an empty string.

        Args:
            wikipedia_url (str): The URL of the Wikipedia page to scrape.
            first_name (str): The first name to search for within the paragraphs.
            last_name (str): The last name to search for within the paragraphs.

        Returns:
            str: The first paragraph containing both the first name and the last name on the Wikipedia page, or an empty string if not found.
        """
        try:
            # Make a GET request to the provided Wikipedia URL
            response = requests.get(wikipedia_url)
            # Raise an exception if the request was unsuccessful
            response.raise_for_status()
            # Parse the response content using BeautifulSoup to navigate the HTML structure
            soup = BeautifulSoup(response.content, 'html.parser')
            # Attempt to find all paragraphs by looking for the 'p' tags within the main content of the page
            # The main content can be identified by the 'mw-content-text' ID or 'mw-parser-output' class
            content = soup.find(id='mw-content-text') or soup.find(class_='mw-parser-output')

            # Find all 'p' tags in the content
            paragraphs = content.find_all('p') if content else []

            first_non_empty_paragraph = None
            # Iterate through the found paragraphs to find the first one that contains both the first name and the last name
            for paragraph in paragraphs:
                # Get the text content of the paragraph, stripping whitespace
                paragraph_text = paragraph.get_text(strip=True)
                # Use a regular expression to remove citation numbers (e.g., [1], [2], etc.)
                clean_text = re.sub(r'\[\d+\]', '', paragraph_text)

                # Store the first non-empty paragraph in case no paragraph containing both names is found
                if not first_non_empty_paragraph and clean_text:
                    first_non_empty_paragraph = clean_text

                # Check if the paragraph contains both the first name and the last name
                if last_name == "None" or last_name is None:
                    if first_name in clean_text:
                        return clean_text
                else:
                    if first_name in clean_text and last_name in clean_text:
                        return clean_text

            # If no paragraph containing both names is found, return the first non-empty paragraph
            if first_non_empty_paragraph:
                return first_non_empty_paragraph
            else:
                # If there are no non-empty paragraphs, log an error and return an empty string
                print(f"No non-empty paragraph found for URL: {wikipedia_url}")
                return ""
        except RequestException as e:
            # If a request exception occurs, log the error and return an empty string
            print(f"An error occurred while getting paragraphs from Wikipedia: {e}")
            return ""

    @tracer.start_as_current_span("to_json_file")
    def to_json_file(self, filepath):
        """
        Saves the collected leaders' data to a JSON file.
        This method opens the specified file in write mode, dumps the leaders_data dictionary
        into the file as JSON, and logs a success message. If an error occurs while writing to the file,
        it logs an error message.

        Args:
            filepath (str): The path to the file where the data should be saved.
        """
        try:
            # Open the specified file in write mode with UTF-8 encoding
            with open(filepath, 'w', encoding='utf-8') as file:
                # Dump the leaders_data dictionary into the file as a JSON-formatted string
                # 'ensure_ascii=False' allows for non-ASCII characters to be written
                # 'indent=4' makes the output more readable by adding indentation to the JSON structure
                json.dump(self.leaders_data, file, ensure_ascii=False, indent=4)
            # Log a success message indicating where the data was saved
            print(f"Data successfully saved to {filepath}")
        except IOError as e:
            # If an IOError occurs (e.g., file not found, permission denied), log an error message with the exception details
            print(f"An error occurred while writing to the file: {e}")
