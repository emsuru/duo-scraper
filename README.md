# Duo Scraper

[![forthebadge made-with-python](https://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

## 📖 Description

The Duo Scraper builds a JSON file with the political leaders of each country found at [this API](https://country-leaders.onrender.com/docs).

The Scraper performs a double scraping task, hence the name "duo":

1. data colection from APIs endpoints:
   
     -- the Scraper first queries a sequence of API endpoints to obtain a list of countries & basic info about their past political leaders.
   
3. data collection from HMTL endpoints:
   
     -- the Scraper then uses the wikipedia urls retrieved from the API to extract & sanitize the leaders' short bios from Wikipedia html pages

The combined information is written in an output JSON file.

## 🛠️ Setup 
   
- Create a new virtual environment by executing this command in your terminal:
   
`python3 -m venv wikipedia_scraper_env`

- Activate the environment by executing this command in your terminal:
   
`source wikipedia_scraper_env/bin/activate`

## ⚙️ Installation

Install the required packages by executing the following command in your terminal:

  ```bash
  pip install -r requirements.txt
  ```
## 👩‍💻 Usage

To run the program, clone this repo on your local machine, then navigate to its directory in your terminal and execute:
```bash
python3 main.py
```

## 📂 Project background

This project was submitted as my second solo project in the AI Bootcamp in Ghent, Belgium, 2024.

Its main goals were to practice:

- using virtual environments
- extracting data from APIs and from HTML
- using exception handling
- getting comfortable with JSON 
- using OOP
- using regex to clean text data

This project was completed over the course of 3 days in February 2024.


![data](https://camo.githubusercontent.com/3fbf9fe8569e07e446820a43eddc4be7841d94c6a977c38379760f36459244b7/68747470733a2f2f692e70696e696d672e636f6d2f6f726967696e616c732f30662f63322f31662f30666332316663643637336637393463316436323232623137373031333334322e706e67)


My main challenges and opportunities to learn while doing the project were:

- handling cookies and sessions when performing GET requests
- handling various tags when parsing html to get the required content

## Extra

As part of the class project's "nice-to-have" requirements, I created a separate repo branch for upgrades called `nice-to-haves`.

I also created a third branch for the project called `feature/o11y` where I experiment with alternative concurrency methods and observability (o11y) via Honeycomb.

Shoutout to [11011](https://github.com/one1zero1one) for his advice and help with these experiments.

## ⚠️ Warning

All my code is currently *heavily*:

- docstringed
- typed
- commented

This is to help me learn and for my feedback sessions with our coach.

---

Thanks for visiting my project page! 

Connect with me on [LinkedIn](https://www.linkedin.com/in/mirunasuru/) 🤍

