# analyzer.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
# Configure the Gemini API with your key
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("🔴 Error: GEMINI_API_KEY not found. Please set it in your .env file.")
    exit()

# Initialize the Generative Model
model = genai.GenerativeModel('gemini-pro')

# --- SAMPLE DATA (We'll replace this with user input later) ---
sample_resume = """
John Doe
Data Analyst

Professional Summary:
A data-driven professional with experience in analyzing datasets to find useful insights.

Experience:
Data Analyst at BizCorp (2022 - Present)
- Looked at sales data to find trends.
- Made reports for management.
- Worked with the sales team.
"""

sample_job_description = """
Senior Data Analyst at TechSolutions Inc.

We are looking for a results-oriented Senior Data Analyst to join our team. The ideal candidate will have a strong background in SQL and Python and a proven track record of optimizing data processes.

Responsibilities:
- Analyze complex datasets using SQL and Python to identify key business insights.
- Develop and maintain dashboards to track performance metrics.
- Present findings to stakeholders in a clear, concise manner.
- Collaborate with engineering to improve data collection processes.
- Quantify the impact of business initiatives, showing improvements in revenue or efficiency.
"""

# --- THE PROMPT TEMPLATE (The "Developer's Magic") ---
prompt_template = f"""
You are an expert career coach and professional resume writer. Your task is to help a user tailor their resume for a specific job.

Analyze the provided RESUME and JOB DESCRIPTION. Then, rewrite the "Professional Summary" and the "Experience" bullet points from the resume to be more impactful and aligned with the job description.

Follow these rules:
1. Use strong, quantifiable action verbs.
2. Incorporate keywords and skills mentioned in the job description (like "SQL", "Python", "stakeholders").
3. Frame the bullet points to show results and achievements, not just duties. For example, instead of "Made reports", use "Developed insightful reports that led to a 10% increase in sales efficiency."

Here is the data:

---
**RESUME:**
{sample_resume}
---
**JOB DESCRIPTION:**
{sample_job_description}
---

Now, provide the rewritten "Professional Summary" and "Experience" sections.
"""

# --- GENERATE THE ANALYSIS ---
print("🤖 Sending request to AI... please wait.")

try:
    response = model.generate_content(prompt_template)
    print("\n--- ✅ AI-POWERED SUGGESTIONS ---\n")
    print(response.text)
except Exception as e:
    print(f"🔴 An error occurred: {e}")