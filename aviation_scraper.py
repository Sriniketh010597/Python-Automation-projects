import pandas as pd  # for creating DataFrames and exporting to Excel/CSV
from datetime import datetime  # to add current date/timestamps
import requests  # to send HTTP requests
import re  # for regex-based text extraction
import os  # for file handling
import tempfile  # to handle fallback saving if permission issues occur


def extract_aviation_data():
    """
    Extract aviation traffic statistics from the Civil Aviation website.
    Uses regex patterns (English/Hindi) and fallbacks to capture values.
    """

    url = "https://www.civilaviation.gov.in/"  # target website
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}  # mimic browser request

    try:
        print("Fetching page...")
        response = requests.get(url, headers=headers, timeout=30)  # send HTTP request
        print(f"Status: {response.status_code}")  # show HTTP response status

        text = response.text  # raw HTML text of the page

        # Save raw HTML locally for debugging in case parsing fails
        with open('raw_response.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Saved raw response to raw_response.txt")

        values = {}  # dictionary to hold extracted values

        # Step 1: Regex patterns for English and Hindi labels
        regex_patterns = {
            'Departing_Flights': [r'Departing flights[^0-9]*(\d[\d,]*)', r'प्रस्थान उड़ानें[^0-9]*(\d[\d,]*)'],
            'Departing_Passengers': [r'Departing Pax[^0-9]*(\d[\d,]*)', r'प्रस्थान यात्री[^0-9]*(\d[\d,]*)'],
            'Arriving_Flights': [r'Arriving flights[^0-9]*(\d[\d,]*)', r'आगमन उड़ानें[^0-9]*(\d[\d,]*)'],
            'Arriving_Passengers': [r'Arriving Pax[^0-9]*(\d[\d,]*)', r'आगमन यात्री[^0-9]*(\d[\d,]*)'],
            'Aircraft_Movements': [r'Aircraft movements[^0-9]*(\d[\d,]*)', r'विमानों की कुल आवाजाही[^0-9]*(\d[\d,]*)'],
            'Airport_Footfalls': [r'Airport footfalls[^0-9]*(\d[\d,]*)', r'हवाई अड्डों पर कुल फुटफॉल[^0-9]*(\d[\d,]*)']
        }

        # Try each regex pattern until a match is found
        for key, pattern_list in regex_patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    num_str = match.group(1).replace(',', '')  # remove commas
                    if num_str.isdigit():
                        values[key] = int(num_str)
                        print(f"Found {key}: {values[key]}")
                        break  # stop after first valid match

        # Step 2: Fallback to Indian number formatting if not all values found
        if len(values) < 6:
            print("\nRegex didn’t capture all values. Trying Indian number format...")

            indian_patterns = {
                'Departing_Flights': r'Departing flights[^0-9]*(\d{1,2},\d{2,3})',
                'Departing_Passengers': r'Departing Pax[^0-9]*(\d{1,2},\d{2},\d{3})',
                'Arriving_Flights': r'Arriving flights[^0-9]*(\d{1,2},\d{2,3})',
                'Arriving_Passengers': r'Arriving Pax[^0-9]*(\d{1,2},\d{2},\d{3})',
                'Aircraft_Movements': r'Aircraft movements[^0-9]*(\d{1,2},\d{2,3})',
                'Airport_Footfalls': r'Airport footfalls[^0-9]*(\d{1,2},\d{2},\d{3})'
            }

            for key, pattern in indian_patterns.items():
                if key not in values:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        values[key] = int(match.group(1).replace(',', ''))
                        print(f"Fallback found {key}: {values[key]}")

        # Step 3: Last fallback - scan Domestic traffic section directly
        if len(values) < 6:
            print("\nFinal fallback - scanning Domestic traffic block...")

            domestic_start = text.find('Domestic traffic')
            international_start = text.find('International traffic')

            if domestic_start != -1 and international_start != -1:
                domestic_section = text[domestic_start:international_start]

                # Find all Indian-style numbers in the domestic section
                all_numbers = re.findall(r'\d{1,2},\d{2,3}(?:,\d{3})*', domestic_section)
                print(f"Numbers found in Domestic section: {all_numbers}")

                if len(all_numbers) >= 6:
                    field_keys = [
                        'Departing_Flights', 'Departing_Passengers', 'Arriving_Flights',
                        'Arriving_Passengers', 'Aircraft_Movements', 'Airport_Footfalls'
                    ]
                    for i, key in enumerate(field_keys):
                        if key not in values and i < len(all_numbers):
                            values[key] = int(all_numbers[i].replace(',', ''))
                            print(f"Mapped {key}: {values[key]}")

        # Step 4: Save results to Excel and CSV
        if len(values) >= 6:
            df_data = {
                'Date': [datetime.now().strftime('%Y-%m-%d')],
                **{k: [v] for k, v in values.items()}
            }

            df = pd.DataFrame(df_data)
            timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            excel_file = f"aviation_data_{timestamp}.xlsx"
            csv_file = f"aviation_data_{timestamp}.csv"

            try:
                df.to_excel(excel_file, index=False)
                df.to_csv(csv_file, index=False)
                print(f"\nSaved to: {excel_file} and {csv_file}")
            except PermissionError:
                temp_dir = tempfile.gettempdir()
                excel_file = os.path.join(temp_dir, f"aviation_data_{timestamp}.xlsx")
                csv_file = os.path.join(temp_dir, f"aviation_data_{timestamp}.csv")
                df.to_excel(excel_file, index=False)
                df.to_csv(csv_file, index=False)
                print(f"\nSaved to temp directory: {excel_file} and {csv_file}")

            print("\nSUCCESS! Extracted values:")
            for k, v in values.items():
                print(f"{k}: {v:,}")  # print with commas for readability

            return df
        else:
            print(f"\nFAILED: Only found {len(values)} values, need 6")
            print("Check raw_response.txt to see what the website actually returned")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    result = extract_aviation_data()
    if result is not None:
        print("\nFinal DataFrame:")
        print(result)
    else:
        print("\nPlease check raw_response.txt to see the actual website content")
