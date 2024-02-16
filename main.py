from src.scraper import WikipediaScraper  # Import the WikipediaScraper class from the scraper module within the src package.

def main() -> None:
    """
    Main function that orchestrates the web scraping process.

    It creates an instance of the WikipediaScraper class, refreshes the session cookie,
    fetches a list of countries, and iterates over each country to fetch and process
    leaders' data. It also saves the scraped data to a JSON file.
    """
    # Create an instance of the WikipediaScraper class.
    # This object will be used to call methods to interact with the web scraping API.
    scraper = WikipediaScraper()

    # Call the refresh_cookie method on the scraper object to obtain a fresh session cookie.
    # This is necessary for authentication with the API during subsequent requests.
    scraper.refresh_cookie()

    # Call the get_countries method on the scraper object to fetch a list of countries from the API.
    # The returned value is stored in the 'countries' variable.
    countries = scraper.get_countries()

    # Check if the 'countries' variable is not None and contains at least one country.
    # This ensures that the following code block only executes if there is data to process.
    if countries:
        # Iterate over each country in the list of countries.
        for country in countries:
            # Call the get_leaders method on the scraper object to fetch leaders' data for the current country.
            # The data is stored within the scraper object's leaders_data attribute.
            scraper.get_leaders(country)
            # Iterate over each leader in the list of leaders for the current country.
            for leader in scraper.leaders_data[country]:
                # Check if the leader has a 'wikipedia_url' key and that it is not empty.
                # This ensures that we only attempt to fetch data for leaders with a valid Wikipedia URL.
                if 'wikipedia_url' in leader and leader['wikipedia_url']:
                    first_paragraph: str = scraper.get_paragraph_containing_names(leader['wikipedia_url'], leader['first_name'], leader['last_name'])
                    leader['first_paragraph'] = first_paragraph
                    print(f"First paragraph for {leader['first_name']} {leader['last_name']}: {first_paragraph}")

    # Test to_json_file method
    filepath = 'leaders_data.json'
    scraper.to_json_file(filepath)
    print(f"Data saved to {filepath}")

if __name__ == "__main__":
    main()
