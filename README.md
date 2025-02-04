# FastAPI Reverse Image Search & PDF Screenshot Service 🚀

This project provides a **FastAPI** application that allows you to upload an image. The service uses **Google Cloud Vision** to perform reverse image search and extract text, and **Selenium** with headless Chrome to capture PDF screenshots of webpages where the image is found. All results are logged to a CSV file. A simple HTML frontend is included to make uploading images easier!

## Features ✨

- **Image Upload** 📤: Easily upload an image using the provided web form.
- **Text Extraction** 🔍: Extract text from the image using the Google Cloud Vision API.
- **Reverse Image Search** 🕵️‍♂️: Identify webpages that include the uploaded image.
- **PDF Screenshot** 📄: Generate PDF screenshots of each matching webpage.
- **CSV Logging** 📝: Log results (timestamp, URL, and PDF filename) into a CSV file.
- **Interactive API Documentation** 📑: Test the endpoint via Swagger UI at `/docs`.

## Requirements 🛠️

- **Python 3.7+**
- [FastAPI](https://fastapi.tiangolo.com/)
- [uvicorn](https://www.uvicorn.org/)
- [Google Cloud Vision API](https://cloud.google.com/vision)
- [Selenium](https://selenium-python.readthedocs.io/)
- [ChromeDriver](https://chromedriver.chromium.org/downloads) (ensure it is in your PATH)
- A valid **Google Cloud credentials** JSON file

## Installation 📥

1. **Clone the Repository:**

```bash
git clone https://github.com/alphatechlogics/WebScraperForImage.git
cd WebScraperForImage
```

2. **Set Up a Virtual Environment (Optional but Recommended):**

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set Up Google Cloud Credentials:**

- On Windows (Command Prompt):

```bash
set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\credentials.json"
```

- On Windows (PowerShell):

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\credentials.json"
```

- On macOS/Linux:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

## Usage 🚀

1. **Run the FastAPI Server:**

```bash
python app.py
```

The server will start on http://localhost:8000.

2. **Access the Frontend:**

- Open your browser and navigate to http://localhost:8000/ to view the simple HTML upload page.

3. **Upload an Image:**

- Use the form to select and upload an image.

- Alternatively, use tools like curl or Postman to send a POST request to /upload.

4. **View Results:**

- The server will extract text, perform a reverse image search, capture PDF screenshots of matching URLs, and log the results to results.csv.
- The JSON response will include the extracted text, details of each processed URL (with timestamp and PDF filename), and the name of the CSV file.

5. **Interactive API Documentation:**

- Visit http://localhost:8000/docs for the Swagger UI and to test endpoints.
