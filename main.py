import sys
import os
import re
import requests
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox, QFileDialog)
from bs4 import BeautifulSoup

class WebScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Web Scraper")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Enter URLs (one per line):")
        layout.addWidget(self.label)
        
        self.url_input = QTextEdit()
        layout.addWidget(self.url_input)
        
        self.output_label = QLabel("Select Output Format:")
        layout.addWidget(self.output_label)
        
        self.format_selector = QComboBox()
        self.format_selector.addItems(["jsonl", "txt"])
        layout.addWidget(self.format_selector)
        
        self.folder_button = QPushButton("Select Output Folder")
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)
        
        self.scrape_button = QPushButton("Start Scraping")
        self.scrape_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.scrape_button)
        
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        self.output_folder = "output"  # Default output folder
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = os.path.join(folder, "output")  # Create an "output" subfolder in the selected directory
            self.status_label.setText(f"Output Folder: {self.output_folder}")
    
    def start_scraping(self):
        urls = self.url_input.toPlainText().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        output_format = self.format_selector.currentText()
        
        if not urls:
            self.status_label.setText("Please enter at least one URL.")
            return
        
        output_path = os.path.join(self.output_folder, output_format)
        os.makedirs(output_path, exist_ok=True)
        
        for url in urls:
            self.scrape_and_process_website(url, output_path, output_format)
        
        self.status_label.setText("Scraping completed!")
    
    def clean_text(self, text):
        """
        Cleans the scraped text by:
        - Removing inline reference numbers (typically superscripted).
        - Stripping extra spaces and special characters.
        - Keeping legal references, case numbers, and dates.
        - Removing instances like `.12` where numbers appear after a period.
        - Ensuring proper spacing between inline elements.
        """
        text = re.sub(r'\s*\d{1,2}(?=[^\w])', '', text)  # Removes inline reference numbers (e.g., "12.")
        text = re.sub(r'(?<=\w)(\d+)(?=\w)', ' ', text)  # Remove numbers between words
        text = re.sub(r'(?<=\.)\d+', '', text)  # Remove numbers that follow a period (e.g., ".12")
        text = re.sub(r'(?<=\w)([A-Z][a-z]+)', r' \1', text)  # Ensure space between different formatted words
        text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
        text = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December),\s(\d{1,2})\b', r'\1 \2', text)  # Fix date formatting
        return text
    
    def scrape_and_process_website(self, url, output_path, output_format):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        case_num = soup.find("title").get_text().replace('.', '').replace(' ', '_').lower()
        filename = case_num
        
        file_path = os.path.join(output_path, filename)
        
        for tag in soup.find_all('a', class_='nt'):
            tag.insert_after(' ')
            tag.decompose()
        
        result_text = []
        for tag in soup.find_all():
            if tag.name == "p" and tag.get("class") == ["b"] and "Footnotes" in tag.text:
                break
            if tag.name == "p":
                cleaned_text = self.clean_text(tag.get_text(separator=" ", strip=True))  # Ensuring proper spacing
                result_text.append(cleaned_text)
        
        final_text = "\n".join(result_text)
        
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebScraperGUI()
    window.show()
    sys.exit(app.exec())