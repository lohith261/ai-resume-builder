import os
import io
import json
import re
import traceback
import fitz  # PyMuPDF
import docx
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from fpdf import FPDF

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load environment variables from .env file
load_dotenv()

# --- AI CONFIGURATION ---
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    # Using a stable and powerful model
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    raise SystemExit(f"🔴 Error during AI configuration: {e}")

# --- HELPER FUNCTIONS FOR FILE EXTRACTION ---
def extract_text_from_pdf(file_stream):
    """Extracts text from a PDF file stream."""
    try:
        pdf_document = fitz.open(stream=file_stream.read(), filetype="pdf")
        text = "".join(page.get_text() for page in pdf_document)
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract_text_from_docx(file_stream):
    """Extracts text from a DOCX file stream."""
    try:
        document = docx.Document(io.BytesIO(file_stream.read()))
        text = "\n".join([para.text for para in document.paragraphs])
        return text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return None

# --- API ENDPOINT FOR RESUME ANALYSIS ---
@app.route('/analyze', methods=['POST'])
def analyze_resume():
    try:
        if 'resume_file' not in request.files:
            return jsonify({"error": "No resume file part"}), 400
        
        file = request.files['resume_file']
        job_description_text = request.form.get('job_description', '')

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not job_description_text:
            return jsonify({"error": "Job description is empty"}), 400

        # Extract text based on file type
        resume_text = ""
        if file.filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file)
        elif file.filename.endswith('.docx'):
            resume_text = extract_text_from_docx(file)
        else:
            return jsonify({"error": "Unsupported file type. Please upload a .pdf or .docx file."}), 400

        if not resume_text:
            return jsonify({"error": "Could not extract text from the file."}), 500

        # Prompt engineered for JSON output
        prompt_template = f"""
        You are an expert resume editor. Analyze the user's RESUME and the target JOB DESCRIPTION.
        Your goal is to provide specific, actionable suggestions to tailor the resume.
        Return your response as a single, valid JSON object with one key: "suggestions".
        The "suggestions" key should contain an array of objects. Each object must have two keys: "original" and "suggestion".
        - "original": The exact text from the resume that should be replaced.
        - "suggestion": The improved text.

        Generate suggestions for the professional summary and for each relevant experience bullet point. Do not make up information.

        RESUME:
        ---
        {resume_text}
        ---
        JOB DESCRIPTION:
        ---
        {job_description_text}
        ---
        """

        response = model.generate_content(prompt_template)
        
        # Clean the response to ensure it's valid JSON
        match = re.search(r'```json\s*(\{.*?\})\s*```', response.text, re.DOTALL)
        if match:
            json_text = match.group(1)
        else:
            json_text = response.text

        suggestions_json = json.loads(json_text)
        return jsonify(suggestions_json)

    except Exception as e:
        print(f"!!! ANALYSIS CRASHED !!!")
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred during analysis."}), 500

# --- API ENDPOINT FOR PDF GENERATION ---
@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get.json()
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' in request body"}), 400

        resume_text = data['text']

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Helvetica', size=11)

        sanitized_text = resume_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, sanitized_text)

        # --- THE FINAL FIX IS HERE ---
        # Explicitly convert the output to a 'bytes' object
        pdf_output = bytes(pdf.output())

        return Response(
            pdf_output,
            mimetype='application/pdf',
            headers={'Content-Disposition': 'attachment;filename=Tailored-Resume.pdf'}
        )
    except Exception as e:
        print(f"!!! PDF GENERATION CRASHED !!!")
        traceback.print_exc()
        return jsonify({"error": "Server crashed during PDF generation. Check terminal for details."}), 500
        
# --- RUN THE SERVER ---
if __name__ == '__main__':
    app.run(debug=True)