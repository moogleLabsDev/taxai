

## Overview
This project is a web scraper that extracts text content from a given website, processes the content into vector embeddings, stores it in a Chroma vector database, and provides an API interface for querying tax regulations using OpenAI's language model.

## Features
- Scrapes all URLs from a specified base URL
- Extracts and cleans text content from webpages
- Splits content into smaller chunks for vector embeddings
- Stores processed data in a Chroma vector database
- Provides a FastAPI-based endpoint to answer user queries using a retrieval-augmented generation (RAG) approach


## Setup and Installation
1. Clone the repo or download the ZIP:
   ```sh
   git clone [github https url]
   cd [github https url]
   
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up OpenAI API key:
   - Add your OpenAI API key  `OPENAI_API_KEY` 

## Usage
### 1. Scraping and Storing Data
- The script starts by defining `get_all_urls()` to fetch all the URLs from the specified website.
- `url_extract()` processes the extracted URLs, transforms the webpage content into text, splits the content, and stores embeddings in a Chroma vector database.
- Data is stored in `url_data.json` for reference.
- First, run the scraping script:
   ```sh
   python3 urlscaping.py
   ```
### 2. Running the API
- To start the FastAPI server, run:
   ```sh
   uvicorn main:app --reload
   ```
- The API exposes an endpoint:
   - `GET /ask?query=your_question` 
   
## API Example
Request:
```sh
curl -X 'GET' 'http://127.0.0.1:8000/ask?query=What are the tax regulations for businesses?' -H 'accept: application/json'
```
Response:
```json
{
    "answer": "[Relevant tax regulation information]",
    "source_titles": ["IRS Tax Guide"]
}
```

## Notes
- Ensure the OpenAI API key is set before running the script.
- The script automatically processes the extracted text into embeddings using OpenAI's model.
- The vector database persists between runs, allowing efficient queries.






