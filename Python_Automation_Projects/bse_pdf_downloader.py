import os  # file system operations
import time  # delays
import requests  # HTTP requests for PDF download
from datetime import datetime  # timestamps
from selenium import webdriver  # Selenium driver
from selenium.webdriver.common.by import By  # element locators
from selenium.webdriver.support.ui import WebDriverWait, Select  # waits & dropdowns
from selenium.webdriver.support import expected_conditions as EC  # wait conditions
from selenium.webdriver.chrome.options import Options  # Chrome options
from selenium.webdriver.common.keys import Keys  # keyboard actions


def setup_chrome_driver():
    """
    Configure and launch Chrome WebDriver with custom download preferences.
    """
    download_dir = os.path.join(os.getcwd(), "ashok_leyland_downloads")  # download folder
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # configure download preferences
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)

    # mask automation
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                     'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    return driver, download_dir


def safe_dropdown_select(driver, dropdown_element, target_text):
    """
    Safely select a dropdown option by exact or partial match.
    """
    try:
        select = Select(dropdown_element)
        options = [option.text.strip() for option in select.options]

        if target_text in options:
            select.select_by_visible_text(target_text)
            return True

        # try partial match
        for option in options:
            if target_text.lower() in option.lower() or option.lower() in target_text.lower():
                select.select_by_visible_text(option)
                return True

        print(f"Dropdown option not found: {target_text}")
        return False

    except Exception as e:
        print(f"Dropdown selection failed: {e}")
        return False


def set_date_field(driver, field_id, date_value):
    """
    Fill a date input field with a given value (JS injection or manual typing).
    """
    try:
        # try JS injection first
        driver.execute_script(f"""
        var field = document.getElementById('{field_id}');
        field.value = '{date_value}';
        field.dispatchEvent(new Event('change'));
        """)
        actual_value = driver.execute_script(f"return document.getElementById('{field_id}').value;")
        if actual_value == date_value:
            return True
    except:
        pass

    try:
        # fallback: manual keyboard input
        field = driver.find_element(By.ID, field_id)
        field.clear()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.DELETE)
        field.send_keys(date_value)
        time.sleep(1)
        field.send_keys(Keys.TAB)
        return True
    except:
        return False


def wait_for_results(driver, timeout=30):
    """
    Wait until search results load after submitting the form.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            rows = driver.find_elements(By.XPATH, "//table//tr[td]")
            if len(rows) > 0:
                return True
            if "no record found" in driver.page_source.lower():
                return True
        except:
            pass
        time.sleep(1)
    return False


def download_pdf_requests(pdf_url, download_dir):
    """
    Download PDF using the requests library.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/pdf,*/*',
            'Referer': 'https://www.bseindia.com/',
        }
        response = requests.get(pdf_url, headers=headers, stream=True, timeout=60)
        if response.status_code == 200:
            filename = f"ashok_leyland_{int(time.time())}.pdf"
            file_path = os.path.join(download_dir, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)
            if os.path.getsize(file_path) > 1000:  # validate size
                return file_path
    except:
        pass
    return None


def fetch_ashok_leyland_pdf():
    """
    Navigate BSE India site and download the latest Ashok Leyland sales PDF.
    """
    driver, download_dir = setup_chrome_driver()
    try:
        driver.get("https://www.bseindia.com/stock-share-price/ashok-leyland-ltd/ashokley/500477/corp-announcements/")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "ddlAnnType")))

        # select equity segment
        segment_dropdown = driver.find_element(By.ID, "ddlAnnType")
        safe_dropdown_select(driver, segment_dropdown, "Equity")
        time.sleep(2)

        # select announcement type
        ann_dropdown = driver.find_element(By.ID, "ddlAnnsubmType")
        safe_dropdown_select(driver, ann_dropdown, "Announcement")
        time.sleep(2)

        # set date range
        set_date_field(driver, "txtFromDt", "01/06/2025")
        set_date_field(driver, "txtToDt", "16/06/2025")
        time.sleep(2)

        # select category
        category_dropdown = driver.find_element(By.ID, "ddlPeriod")
        safe_dropdown_select(driver, category_dropdown, "Company Update")
        time.sleep(3)

        # select subcategory
        subcat_dropdown = driver.find_element(By.ID, "ddlsubcat")
        subcat_options = [opt.text for opt in Select(subcat_dropdown).options]
        for opt in subcat_options:
            if "monthly" in opt.lower() and "business" in opt.lower():
                safe_dropdown_select(driver, subcat_dropdown, opt)
                break
        time.sleep(2)

        # submit form
        submit_btn = driver.find_element(By.ID, "btnSubmit")
        driver.execute_script("arguments[0].click();", submit_btn)
        wait_for_results(driver)
        time.sleep(5)

        # check for PDF links
        pdf_links = driver.find_elements(By.XPATH, "//a[i[contains(@class, 'fa-file-pdf-o')]]")
        target_keywords = ["may", "2025", "sales", "monthly", "business"]

        for link in pdf_links:
            try:
                href = link.get_attribute('href')
                row_text = ""
                try:
                    row_text = link.find_element(By.XPATH, "./ancestor::tr[1]").text.lower()
                except:
                    pass

                if any(kw in row_text for kw in target_keywords):
                    result = download_pdf_requests(href, download_dir)
                    if result:
                        return result
            except Exception as e:
                print(f"Error extracting PDF: {e}")
                continue

        return None

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()


if __name__ == "__main__":
    start_time = datetime.now()
    pdf_file = fetch_ashok_leyland_pdf()
    end_time = datetime.now()

    if pdf_file:
        print(f"PDF downloaded: {pdf_file}")
    else:
        print("PDF not found in the given date range")

    print(f"Total time: {(end_time - start_time).total_seconds():.1f} seconds")
