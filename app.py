import io
import csv
import time
import base64
from datetime import datetime
from google.cloud import vision
from google.oauth2 import service_account
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Define the path to your credentials file
credentials_path = "credentials.json"

# Load the credentials and create a credentials object
credentials = service_account.Credentials.from_service_account_file(
    credentials_path)


def reverse_image_search(image_path):
    """
    Uses Google Cloud Vision API’s web detection to perform a reverse image search
    and return a list of URLs of pages with matching images.
    """
    # Pass the credentials to the client
    client = vision.ImageAnnotatorClient(credentials=credentials)

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # Call the Vision API for web detection.
    response = client.web_detection(image=image)
    annotations = response.web_detection

    urls = []
    if annotations.pages_with_matching_images:
        for page in annotations.pages_with_matching_images:
            urls.append(page.url)
    else:
        print("No matching pages found.")

    if response.error.message:
        raise Exception(f'Error from Vision API: {response.error.message}')

    return urls


def extract_text_from_image(image_path):
    """
    Uses Vision API’s text detection to extract any text present in the image.
    """
    # Pass the credentials to the client
    client = vision.ImageAnnotatorClient(credentials=credentials)

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        # The first annotation usually contains all the detected text.
        return texts[0].description
    else:
        return ""


def save_page_as_pdf(driver, url, output_path):
    """
    Loads the given URL in Selenium’s headless browser and then uses the
    Chrome DevTools Protocol command 'Page.printToPDF' to save a PDF of the page.
    """
    driver.get(url)
    # Wait a few seconds to allow the page to load completely.
    time.sleep(5)
    # Generate a PDF of the page. The 'printBackground' flag ensures background graphics are included.
    pdf = driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
    pdf_data = base64.b64decode(pdf['data'])
    with open(output_path, 'wb') as f:
        f.write(pdf_data)
    return output_path


def main():
    image_file_path = "test1.jpg"   #"test1.jpg"   Replace with your image file path

    # (Optional) Extract text from the image.
    extracted_text = extract_text_from_image(image_file_path)
    if extracted_text:
        print("Extracted text from image:")
        print(extracted_text)
    else:
        print("No text detected in the image.")

    # Perform the reverse image search.
    try:
        matching_urls = reverse_image_search(image_file_path)
    except Exception as e:
        print(f"Error during reverse image search: {e}")
        return

    if not matching_urls:
        print("No matching URLs found.")
        return

    print("Found the following URLs:")
    for url in matching_urls:
        print(url)

    # Set up headless Chrome using Selenium.
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    # If chromedriver isn’t in your PATH, specify its location via the executable_path parameter.
    driver = webdriver.Chrome(options=chrome_options)

    # Open a CSV file to record the results.
    csv_filename = "results.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['timestamp', 'url', 'pdf_filename']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for url in matching_urls:
            try:
                # Create a timestamp for naming the PDF.
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_filename = f"screenshot_{timestamp}.pdf"
                # Save the webpage as a PDF.
                save_page_as_pdf(driver, url, pdf_filename)
                # Write the details to the CSV.
                writer.writerow({
                    'timestamp': timestamp,
                    'url': url,
                    'pdf_filename': pdf_filename
                })
                print(f"Saved PDF for {url} as {pdf_filename}")
            except Exception as e:
                print(f"Failed to process {url}: {e}")

    driver.quit()
    print(f"Results saved to {csv_filename}")


if __name__ == "__main__":
    main()
