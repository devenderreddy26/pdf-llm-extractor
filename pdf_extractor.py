import fitz  # pymupdf
import pytesseract
from pdf2image import convert_from_path
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# CONFIGURATION
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================================
# STRATEGY 1: EDITABLE FORMS (Spatial Merge)
# ==========================================
def clean_widget_value(widget):
    val = widget.field_value
    if val is None: return ""
    val_str = str(val)
    if val_str in ['/Yes', '/On', 'Yes', 'On']: return "[Checked]"
    if val_str in ['/Off', 'Off']: return "[ ]"
    return val_str

def extract_form_spatially(doc):
    full_text = ""
    print("  -> Strategy: Spatial Merge (Editable Form)")
    
    for page_num, page in enumerate(doc):
        items = []
        
        # 1. Get Static Text
        for w in page.get_text("words"):
            items.append({
                'x0': w[0], 'y': w[1], 'text': w[4], 'type': 'text'
            })
            
        # 2. Get Widget Values
        for widget in page.widgets():
            val = clean_widget_value(widget)
            if val:
                items.append({
                    'x0': widget.rect.x0, 'y': widget.rect.y0, 
                    'text': f"**{val}**", 'type': 'field'
                })
        
        # 3. Sort Spatially (Top-down, Left-right)
        items.sort(key=lambda x: (round(x['y'], 1), x['x0']))
        
        # 4. Reconstruct Page
        page_text = ""
        last_y = 0
        for item in items:
            if last_y == 0: last_y = item['y']
            
            # New line detection (>10px difference)
            if item['y'] > last_y + 10:
                page_text += "\n"
                last_y = item['y']
            
            page_text += item['text'] + " "
            
        full_text += f"\n--- Page {page_num+1} ---\n{page_text}\n"
        
    return full_text

# ==========================================
# STRATEGY 2: SCANNED IMAGES (OCR)
# ==========================================
def extract_ocr(pdf_path):
    print("  -> Strategy: OCR (Scanned Image)")
    text = ""
    try:
        images = convert_from_path(pdf_path, dpi=300)
        for i, img in enumerate(images):
            # psm 6 = Assume a single uniform block of text
            page_text = pytesseract.image_to_string(img, config='--psm 6')
            text += f"\n--- Page {i+1} (OCR) ---\n{page_text}\n"
    except Exception as e:
        return f"Error running OCR: {str(e)}. Check Poppler/Tesseract installation."
    return text

# ==========================================
# STRATEGY 3: STANDARD DIGITAL TEXT
# ==========================================
def extract_standard_text(doc):
    print("  -> Strategy: Standard Text Extraction")
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

# ==========================================
# MASTER CONTROLLER
# ==========================================
def process_pdf(pdf_path):
    print(f"Processing: {pdf_path}...")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return f"Error opening PDF: {e}"
    
    # 1. Check for Editable Forms (Widgets)
    has_forms = any(page.widgets() for page in doc)
    
    # 2. Check for Content Layer (Text)
    first_page_text = doc[0].get_text() if len(doc) > 0 else ""
    is_scanned = len(first_page_text.strip()) < 50
    
    if has_forms:
        return extract_form_spatially(doc)
    elif is_scanned:
        doc.close() 
        return extract_ocr(pdf_path)
    else:
        return extract_standard_text(doc)

# ==========================================
# LLM INTERFACE
# ==========================================
def ask_llm(context_text, user_question):
    print("\nSending to OpenAI...")
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY not found in .env file."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant. Use the provided document text to answer the user's question. If the document has form fields, user inputs are bolded like **this**."
                },
                {
                    "role": "user", 
                    "content": f"Document Content:\n{context_text}\n\nQuestion: {user_question}"
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM Error: {e}"

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # Change this to your test file
    my_pdf = "sample_form.pdf" 
    
    # Check if file exists
    if not os.path.exists(my_pdf):
        print(f"File {my_pdf} not found. Please add a PDF to test.")
    else:
        # 1. Extract
        extracted_data = process_pdf(my_pdf)
        
        # 2. Preview
        print("\n--- EXTRACTED CONTENT PREVIEW ---")
        print(extracted_data[:500] + "...") 
        
        # 3. Ask Question
        question = "Who is the vendor and what is the total amount?"
        answer = ask_llm(extracted_data, question)
        
        print("\n--- LLM ANSWER ---")
        print(answer)
