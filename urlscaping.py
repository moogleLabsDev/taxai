import os
import requests
from langchain_openai import OpenAIEmbeddings 
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.vectorstores import Chroma
import re
import json
from datetime import datetime


# Defining Splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50
)
embeddings = OpenAIEmbeddings(openai_api_key="")

# Extracting all URLs in the given site.
def get_all_urls(base_url):
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = soup.find_all('a', href=True)
        # Initialize a set and add the base_url
        urls = set()
        urls.add(base_url)  # Ensure base_url is included
        for link in all_links:
            href = link['href']
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            # Include only valid URLs with a non-empty path
            if parsed_url.scheme and parsed_url.netloc and parsed_url.path:
                urls.add(full_url)
        return urls
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return {base_url}  # Return a set containing only base_url in case of failure
        
def store_json(docs_transformed, collection_name, filename="url_data.json"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Extract the text content from the transformed docs
    docs_text = [doc.page_content for doc in docs_transformed]  # assuming docs_transformed is a list of Document objects
    data = {"data": docs_text, "collection_name": collection_name, "timestamp": timestamp}

    # Check if file exists
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            existing_data = json.load(f)
        existing_data.append(data)
        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=4)
    else:
        with open(filename, 'w') as f:
            json.dump([data], f, indent=4)
    print(f"Data saved to {filename}.")

# Extracting all the text and making the embedding..
def url_extract(all_urls, persist_directory, collection_name):
    # vectordb = Chroma(persist_directory=persist_directory,embedding_function=embeddings)
    # vectordb.delete_collection()
    # vectordb.persist()
    print("Total link found = ", len(all_urls))
    print(f"Extracting all {collection_name} Links.")
    print("Please Wait.....")
    for i,  url in enumerate(all_urls):
        print(collection_name)
        try:
            loader = AsyncHtmlLoader(url)
            html = loader.load()
            if not html or 'error' in html:
                print(f"Error: Empty or invalid HTML content for {url}")
                continue
            html2text = Html2TextTransformer()
            docs_transformed = html2text.transform_documents(html)
            splits = splitter.split_documents(docs_transformed)
            print(f'{i+1}/{len(all_urls)} Length of document of {url} : ', len(splits)) 
            vectordb = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_directory, collection_name=collection_name)
            store_json(docs_transformed, collection_name)
        except Exception as e:
            print(f"Error in link {url}: {e}")
    print("Hold On for embedding generation...")       
    print('Total length of vectordb ',vectordb._collection.count())
    return vectordb   
  
def url_clean(name: str) -> str:
    # Replace all non-alphanumeric characters (except spaces) with underscore
    cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '_', name)
    # Replace spaces with underscores
    cleaned_name = cleaned_name.replace(' ', '_')
    return cleaned_name

# Extracting URLs
url = "https://www.irs.gov/privacy-disclosure/tax-code-regulations-and-official-guidance"
all_urls = get_all_urls(url)
# Print the list of URLs
print("All URLs on the page:", all_urls)
print('Ttal Number of Links Found', len(all_urls))

persist_directory = 'TaxAI2'
# collection =url.split("https://www.irs.gov/")[1]
collection_name = 'TaxAI'  #url_clean(collection)
vectordb = url_extract(all_urls, persist_directory, collection_name)
