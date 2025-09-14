# Python-Automation-projects
This repository is a collection of Python scripting and automation projects built to extract, process, and transform data from real-world sources. The projects are focused on web scraping, PDF parsing, data cleaning, and automated reporting. They highlight how Python can reduce manual effort and streamline repetitive workflows.

## Purpose 
The purpose of this repository is to demonstrate how Python can be applied to real-world automation tasks. Each project shows a different aspect of automation — from downloading and parsing PDF reports, to scraping live websites, to structuring data into usable formats.

The key goals are:

1. To automate repetitive tasks that would otherwise require manual effort.

2. To extract insights from unstructured sources such as PDFs and websites.

3. To provide reusable templates for common automation workflows like scraping, parsing, and reporting.

4. To highlight the versatility of Python for solving problems across industries, including finance, transportation, and business reporting.

## Projects Included
1. Aviation Statistics Scraper (aviation_scraper.py)

Scrapes daily aviation statistics from the Civil Aviation Ministry website. Captures key data points such as:

* Departing flights

* Arriving flights

* Passenger counts (Departing & Arriving)

* Aircraft movements

* Airport footfalls

* Handles multilingual text (English & Hindi) and Indian number formats (e.g., 4,16,477).

* Saves results to Excel and CSV with timestamps for tracking.

2. BSE Ashok Leyland PDF Downloader (bse_pdf_downloader.py)

Automates the BSE India corporate announcements portal. Uses Selenium to:

* Navigate dropdown filters (Equity → Announcements → Company Updates).
* Select custom date ranges.
* Identify relevant “Monthly Business/Sales Update” announcements.
* Downloads the latest Ashok Leyland monthly PDF reports.
* Saves them locally in a structured folder.

3. Ashok Leyland Sales Parser (sales_parser.py)

Reads the Ashok Leyland PDF reports downloaded above. Extracts only the Domestic Sales block (ignores other data). Cleans and structures the table with headers:

* Category
* Monthly sales (May ’25 vs May ’24)
* Increment/Decrement
* Cumulative values
* Exports neatly into Excel with:
* Bold, centered headers
* Auto-adjusted column widths
* Consistent formatting for readability

## Tools & Technologies

* Python 3.9+

Libraries Used:

* selenium → Web browser automation

* pandas → Data manipulation & export

* pdfplumber → Extracting tables from PDFs

* openpyxl → Excel formatting

* requests → HTTP requests & file downloads

* re → Regex for text/number pattern matching
