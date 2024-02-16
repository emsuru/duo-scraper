# wikipedia-scraper 🚧 WORK-IN-PROGRESS 🚧
This program queries an API to obtain a list of countries and their past political leaders. It then extracts & sanitizes their short bios from Wikipedia. Finally,the program then saves the data to disk.

to create the env:
`python3 -m venv wikipedia_scraper_env`

to activate the envv:
`source wikipedia_scraper_env/bin/activate`

## Installation

To install the required packages, run the following command:

  ```bash
  pip3 install -r requirements.txt
  ```
## Usage

To run the program, execute the following command:

  ```bash
  export OTEL_SERVICE_NAME="wikipedia-scraper"
  export HONEYCOMB_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # get your free key from https://ui.honeycomb.io/
  opentelemetry-instrument python3 main.py
  ```
