import io
import csv
import time
import base64
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from google.cloud import vision
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from fastapi.staticfiles import StaticFiles

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


def reverse_image_search_bytes(image_bytes: bytes):
    print("[INFO] Starting reverse image search...")
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.web_detection(image=image)
    annotations = response.web_detection

    urls = []
    if annotations.pages_with_matching_images:
        for page in annotations.pages_with_matching_images:
            urls.append(page.url)
        print(f"[INFO] Found {len(urls)} matching page(s).")
    else:
        print("[WARN] No matching pages found.")

    if response.error.message:
        raise Exception(f"Error from Vision API: {response.error.message}")
    return urls


def extract_text_from_image_bytes(image_bytes: bytes):
    print("[INFO] Extracting text from image...")
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        extracted_text = texts[0].description
        print("[INFO] Text extraction complete.")
        return extracted_text
    else:
        print("[INFO] No text found in the image.")
        return ""


def save_page_as_pdf(driver, url, output_path):
    print(f"[INFO] Navigating to URL: {url}")
    try:
        # Set a page load timeout (in seconds)
        driver.set_page_load_timeout(60)
        driver.get(url)
    except TimeoutException:
        print(f"[WARN] Page load timeout for {url}. Attempting to stop page loading.")
        try:
            driver.execute_script("window.stop();")
        except Exception as e_stop:
            print(f"[ERROR] Unable to stop page load for {url}: {e_stop}")
    except Exception as e:
        print(f"[ERROR] Exception during driver.get for {url}: {e}")
        try:
            driver.execute_script("window.stop();")
        except Exception as e_stop:
            print(f"[ERROR] Unable to stop page load for {url}: {e_stop}")

    # Wait a few seconds to ensure that dynamic content is loaded
    time.sleep(5)
    print("[INFO] Generating PDF screenshot...")
    try:
        pdf = driver.execute_cdp_cmd(
            "Page.printToPDF", {"printBackground": True})
        pdf_data = base64.b64decode(pdf["data"])
        with open(output_path, "wb") as f:
            f.write(pdf_data)
        print(f"[INFO] PDF saved as: {output_path}")
    except Exception as e:
        print(f"[ERROR] Error generating PDF for {url}: {e}")
        raise e

    return output_path


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    print("[INFO] Received file upload.")
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    try:
        print("[INFO] Reading file bytes...")
        image_bytes = await file.read()
        print("[INFO] File read successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to read file: {e}")

    try:
        extracted_text = extract_text_from_image_bytes(image_bytes)
    except Exception as e:
        extracted_text = ""
        print(f"[ERROR] Error extracting text: {e}")

    try:
        matching_urls = reverse_image_search_bytes(image_bytes)
    except Exception as e:
        print(f"[ERROR] Error in reverse image search: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error in reverse image search: {e}")

    if not matching_urls:
        print("[INFO] No matching URLs found.")
        return JSONResponse(
            status_code=200,
            content={
                "message": "No matching URLs found.",
                "extracted_text": extracted_text,
                "results": [],
            },
        )

    # Set up headless Chrome using Selenium.
    print("[INFO] Setting up headless Chrome with Selenium...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    print("[INFO] Headless Chrome initiated.")

    results = []
    csv_filename = "results.csv"

    # Open CSV file for writing results.
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["timestamp", "url", "pdf_filename"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for url in matching_urls:
            print(f"[INFO] Processing URL: {url}")
            ts = datetime.now()
            # CSV timestamp formatted as "YYYY-MM-DD HH:MM:SS"
            ts_csv = ts.strftime("%Y-%m-%d %H:%M:%S")
            # PDF filename timestamp formatted as "YYYYMMDD_HHMMSS"
            ts_pdf = ts.strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"screenshot_{ts_pdf}.pdf"

            try:
                save_page_as_pdf(driver, url, pdf_filename)
                result = {"timestamp": ts_csv, "url": url,
                          "pdf_filename": pdf_filename}
                print(f"[INFO] Processed URL successfully: {url}")
            except Exception as e:
                result = {"timestamp": ts_csv, "url": url,
                          "pdf_filename": f"Error: {e}"}
                print(f"[ERROR] Failed to process URL: {url} - Error: {e}")

            writer.writerow(result)
            results.append(result)

    driver.quit()
    print("[INFO] Completed processing all URLs. Headless Chrome closed.")
    print("[INFO] Results logged to CSV file.")

    return JSONResponse(
        status_code=200,
        content={
            "message": "Processing complete.",
            "extracted_text": extracted_text,
            "results": results,
            "csv_file": csv_filename,
        },
    )


if __name__ == "__main__":
    import uvicorn
    print("[INFO] Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
