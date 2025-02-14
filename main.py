import os
import requests
from bs4 import BeautifulSoup
import json

# File path with folder structure
folder_path = "output/"

def scrape_and_process_website(url, output_format="jsonl"):
    # Step 1a: Fetch the webpage content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Step 1b: Get the Case Number for the file name
    case_num = soup.find("title").get_text().replace('.', '').replace(' ', '_').lower()
    filename = case_num

    # Step 1c: Create the subfolders
    file_path = os.path.join(folder_path+output_format,filename)  
    os.makedirs(folder_path + output_format, exist_ok=True)
    
    # Step 2a: Remove all superscripts
    for tag in soup.find_all('a', class_='nt'):
        tag.insert_after(' ')  # Insert a space before the tag
        tag.decompose()  # Removes the tag from the tree

    # Step 2b: Extract relevant content
    result_text = []
    for tag in soup.find_all():
        # Stop at the <p class="b">Footnotes</p> section
        if tag.name == "p" and tag.get("class") == ["b"] and "Footnotes" in tag.text:
            break
        # Collect text if it's not inside the "Footnotes" section
        if tag.name == "p":
            result_text.append(tag.get_text(strip=True))

    # Combine the extracted text
    final_text = "\n".join(result_text)

    # Step 3: Preprocess the content
    if output_format == "txt":
        
        with open(file_path + ".txt", "w", encoding="utf-8") as file:

            for line in final_text.split("\n"):
                if line.strip():
                    file.write(line.strip() + "\n")
            
    elif output_format == "jsonl":
        with open(file_path + ".jsonl", "w", encoding="utf-8") as file:
            for line in final_text.split("\n"):
                if line.strip():
                    json.dump({"text": line.strip()}, file)
                    file.write("\n")

# ADD URLS
urls = ["https://lawphil.net/judjuris/juri2023/mar2023/gr_198201_2023.html", "https://lawphil.net/judjuris/juri2023/nov2023/gr_241844_2023.html", "https://lawphil.net/judjuris/juri2023/oct2023/am_ca-24-002-p_2023.html","https://lawphil.net/judjuris/juri2023/oct2023/gr_262122_2023.html", "https://lawphil.net/judjuris/juri2023/jan2023/gr_136506_2023.html","https://lawphil.net/judjuris/juri2023/jan2023/gr_258424_2023.html","https://lawphil.net/judjuris/juri2023/aug2023/gr_258060_2023.html", "https://lawphil.net/judjuris/juri2023/aug2023/ac_8367_2023.html", "https://lawphil.net/judjuris/juri2023/apr2023/gr_244027_2023.html", "https://lawphil.net/judjuris/juri2023/apr2023/gr_252790_2023.html", "https://lawphil.net/judjuris/juri2023/jun2023/gr_234614_2023.html", "https://lawphil.net/judjuris/juri2023/nov2023/gr_265272_2023.html", "https://lawphil.net/judjuris/juri2023/nov2023/gr_262889_2023.html", "https://lawphil.net/judjuris/juri2023/nov2023/ac_11026_2023.html", "https://lawphil.net/judjuris/juri2023/jul2023/gr_209479_2023.html"]

# BATCH APPLY
for url in urls:
    scrape_and_process_website(url, output_format="jsonl")
    scrape_and_process_website(url, output_format="txt")