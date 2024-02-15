from src.scraper import WikipediaScraper  # Import the WikipediaScraper class from the scraper module within the src package.
from opentelemetry import trace

tracer = trace.get_tracer("mytracer")

@tracer.start_as_current_span("main")
def main():
    # Create an instance of the WikipediaScraper class.
    # This object will be used to call methods to interact with the web scraping API.
    scraper = WikipediaScraper()

    # Call the refresh_cookie method on the scraper object to obtain a fresh session cookie.
    # This is necessary for authentication with the API during subsequent requests.
    scraper.refresh_cookie()
    # Print the value of the cookie to verify that it has been refreshed and is stored in the scraper object.
    print(f"Cookie: {scraper.cookie}")

    # Call the get_countries method on the scraper object to fetch a list of countries from the API.
    # The returned value is stored in the 'countries' variable.
    countries = scraper.get_countries()
    # Print the list of countries to verify that the data has been fetched successfully.
    print(f"Countries: {countries}")

    # Check if the 'countries' variable is not None and contains at least one country.
    # This ensures that the following code block only executes if there is data to process.
    if countries:
        # Iterate over each country in the list of countries.
        for country in countries:
            # Call the get_leaders method on the scraper object to fetch leaders' data for the current country.
            # The data is stored within the scraper object's leaders_data attribute.
            scraper.get_leaders(country)
            # Print the leaders' data for the current country to verify that it has been fetched successfully.
            print(f"Leaders of {country}: {scraper.leaders_data[country]}")

            # Iterate over each leader in the list of leaders for the current country.
            for leader in scraper.leaders_data[country]:
                # Check if the leader has a 'wikipedia_url' key and that it is not empty.
                # This ensures that we only attempt to fetch data for leaders with a valid Wikipedia URL.
                if 'wikipedia_url' in leader and leader['wikipedia_url']:
                    first_paragraph = scraper.get_paragraph_containing_names(leader['wikipedia_url'], leader['first_name'], leader['last_name'])
                    leader['first_paragraph'] = first_paragraph
                    print(f"First paragraph for {leader['first_name']} {leader['last_name']}: {first_paragraph}")

    # Test to_json_file method
    filepath = 'leaders_data.json'
    scraper.to_json_file(filepath)
    print(f"Data saved to {filepath}")

if __name__ == "__main__":
    main()
