# pdf-llm-extractor
pdf-llm-extractor
# PDF to LLM Extractor

A robust Python pipeline that extracts text from any type of PDF (Editable Forms, Digital Docs, or Scanned Images) and prepares it for search using OpenAI's LLM.

## Features
- **Smart Detection:** Automatically detects if a PDF is a fillable form, a standard document, or a flat scan.
- **Form Handling:** Extracts "hidden" values from editable widgets (AcroForms) and merges them spatially with background text.
- **OCR Integration:** Uses Tesseract to handle scanned/flattened documents.
- **LLM Ready:** Outputs clean, structured text ready for RAG (Retrieval Augmented Generation) or direct context injection.

## Prerequisites

Before running the Python script, you must install these external tools:

### 1. Tesseract OCR
Required for scanned documents.
- **Windows:** [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Add to PATH during installation).
- **Mac:** `brew install tesseract`
- **Linux:** `sudo apt-get install tesseract-ocr`

### 2. Poppler
Required by `pdf2image` to convert PDF pages to images.
- **Windows:** [Download Release](https://github.com/oschwartz10612/poppler-windows/releases/), extract, and add the `bin` folder to your System PATH.
- **Mac:** `brew install poppler`
- **Linux:** `sudo apt-get install poppler-utils`

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/pdf-llm-extractor.git](https://github.com/YOUR_USERNAME/pdf-llm-extractor.git)
   cd pdf-llm-extractor


How It Works
Ingestion: The script opens the PDF using pymupdf.

Analysis: It checks for form widgets or low text density (indicating a scan).

Extraction:

Forms: Extracts widget values and inserts them into the text stream at their visual coordinates.

Scans: Converts pages to images and runs Tesseract OCR.

Standard: Extracts text normally.

Query: Sends the combined context to GPT-4o to answer your questions.
