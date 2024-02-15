from src.scraper import WikipediaScraper  # Import the WikipediaScraper class from the scraper module within the src package.
from opentelemetry import trace, context
import concurrent.futures

tracer = trace.get_tracer("mytracer")

def process_country(country, scraper, parent_context):
    token = context.attach(parent_context)
    try:
        with tracer.start_as_current_span("each_country"):
            current_span = trace.get_current_span()
            print(f"Processing country: {country}, Current Span ID: {current_span.get_span_context().span_id}, Trace ID: {current_span.get_span_context().trace_id}")
            current_span.set_attribute("country", country)
            scraper.get_leaders(country)
            #print(f"Leaders of {country}: {scraper.leaders_data[country]}")

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor2:
                # Capture the current context
                parent_context = context.get_current()
                # Pass the captured context along with other arguments
                futures = []
                for leader in scraper.leaders_data[country]:
                    future = executor2.submit(process_leader, leader, scraper, parent_context)
                    process_leader(leader, scraper, context.get_current())
                    futures.append(future)
                concurrent.futures.wait(futures)

    finally:
        context.detach(token)                

def process_leader(leader, scraper, parent_context):
    token = context.attach(parent_context)
    try:
        with tracer.start_as_current_span("process_leader"):
            if 'wikipedia_url' in leader and leader['wikipedia_url']:
                first_paragraph = scraper.get_paragraph_containing_names(leader['wikipedia_url'], leader['first_name'], leader['last_name'])
                leader['first_paragraph'] = first_paragraph
                #print(f"First paragraph for {leader['first_name']} {leader['last_name']}: {first_paragraph}")
    finally:
        context.detach(token)                

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
    with tracer.start_as_current_span("get_countries"):
        countries = scraper.get_countries()
    # Print the list of countries to verify that the data has been fetched successfully.
    print(f"Countries: {countries}")

    # Check if the 'countries' variable is not None and contains at least one country.
    # This ensures that the following code block only executes if there is data to process.
    # No changes needed here for capturing the context before submitting tasks
    if countries:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Capture the current context
            parent_context = context.get_current()
            # Pass the captured context along with other arguments
            futures = []
            for country in countries:
                future = executor.submit(process_country, country, scraper, parent_context)
                futures.append(future)
            concurrent.futures.wait(futures)

    # Test to_json_file method
    filepath = 'leaders_data.json'
    scraper.to_json_file(filepath)
    print(f"Data saved to {filepath}")

if __name__ == "__main__":
    main()
