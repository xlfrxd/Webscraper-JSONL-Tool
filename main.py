import sys
import os
import re
import requests
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox, QFileDialog)
from PyQt6.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup

class ScraperThread(QThread):
    progress_signal = pyqtSignal(str)  # Signal to update UI status

    def __init__(self, urls, output_folder, output_format):
        super().__init__()
        self.urls = urls
        self.output_folder = output_folder
        self.output_format = output_format

    def run(self):
        output_path = os.path.join(self.output_folder, self.output_format)
        os.makedirs(output_path, exist_ok=True)

        for url in self.urls:
            try:
                self.progress_signal.emit(f"Scraping: {url}")
                self.scrape_and_process_website(url, output_path)
            except Exception as e:
                self.progress_signal.emit(f"Error scraping {url}: {str(e)}")

        self.progress_signal.emit("Scraping completed!")

    def scrape_and_process_website(self, url, output_path):
        try:
            response = requests.get(url, timeout=10)  # Set a timeout of 10 seconds
            response.raise_for_status()  # Raise exception for HTTP errors
        except requests.exceptions.RequestException as e:
            self.progress_signal.emit(f"Failed to fetch {url}: {str(e)}")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("title")
        case_num = title_tag.get_text().replace('.', '').replace(' ', '_').lower() if title_tag else "untitled_case"
        filename = os.path.join(output_path, case_num)

        for tag in soup.find_all('a', class_='nt'):
            tag.insert_after(' ')
            tag.decompose()

        result_text = []
        for tag in soup.find_all():
            if tag.name == "p" and tag.get("class") == ["b"] and "Footnotes" in tag.text:
                break
            if tag.name == "p":
                cleaned_text = self.clean_text(tag.get_text(separator=" ", strip=True))
                result_text.append(cleaned_text)

        final_text = "\n".join(result_text)

        if self.output_format == "txt":
            with open(filename + ".txt", "w", encoding="utf-8") as file:
                file.write(final_text)
        elif self.output_format == "jsonl":
            with open(filename + ".jsonl", "w", encoding="utf-8") as file:
                for line in final_text.split("\n"):
                    json.dump({"text": line.strip()}, file)
                    file.write("\n")

    def clean_text(self, text):
        """ Cleans and formats text while preserving legal references. """
        text = re.sub(r'(?<=\.)\d+', '', text)  # Remove numbers after a period
        text = re.sub(r'(?<=\w)([A-Z][a-z]+)', r' \1', text)  # Ensure space between words
        text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
        text = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December),\s(\d{1,2})\b', r'\1 \2', text)  # Fix date formatting
        return text

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
            self.output_folder = os.path.join(folder, "output")
            self.status_label.setText(f"Output Folder: {self.output_folder}")

    def start_scraping(self):
        urls = self.url_input.toPlainText().split('\n')
        urls = [url.strip() for url in urls if url.strip()]
        output_format = self.format_selector.currentText()

        if not urls:
            self.status_label.setText("Please enter at least one URL.")
            return

        self.scraper_thread = ScraperThread(urls, self.output_folder, output_format)
        self.scraper_thread.progress_signal.connect(self.update_status)
        self.scraper_thread.start()

    def update_status(self, message):
        self.status_label.setText(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebScraperGUI()
    window.show()
    sys.exit(app.exec())
