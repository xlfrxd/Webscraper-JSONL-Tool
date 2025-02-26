# Webscraper-JSONL Tool

Scrape text from websites and convert it into JSONL files. This tool prepares text files for annotation in Doccano or any other annotation tool.

## Setup

### 1. Create a Python Environment in VS Code
To ensure a clean workspace, set up a Python environment in Visual Studio Code.

### 2. Install Dependencies
Run the following command to install the required dependencies:

```sh
pip install pyqt6 requests bs4
```

## Usage

1. **Enter URLs**: Input one or multiple URLs in the text field.
2. **Select Output Format**: Choose JSONL or TXT format for the scraped data.
3. **Select Output Folder**: Set the directory where files will be saved.
4. **Start Scraping**: Click the scrape button to begin extracting data.
5. **Monitor Progress**: View status updates in the application UI.

## Features
- **Multi-URL Support**: Scrape multiple websites in one session.
- **Asynchronous Processing**: Uses multithreading to prevent UI freezing.
- **Timeout Handling**: Skips slow-loading pages after a set time.
- **Formatted Output**: Saves cleaned and structured text in JSONL format.

## Compatibility
- Python 3.x
- Windows, macOS, Linux

## Contributing
Feel free to submit issues or suggest improvements as this tool is open for enhancements.