# Image to Text Table Converter

This application converts text from images into a 6-row table format using OCR (Optical Character Recognition).

## Prerequisites

Before running the application, you need to install Tesseract OCR:

### On macOS:
```bash
brew install tesseract
```

### On Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr
```

### On Windows:
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add the installation directory to your system PATH

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On macOS/Linux:
```bash
source venv/bin/activate
```
- On Windows:
```bash
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To run the Streamlit application:
```bash
streamlit run main.py
```

The application will open in your default web browser. You can then:
1. Upload an image containing text
2. Click "Extract Text" to process the image
3. View the extracted text in a 6-row table format 