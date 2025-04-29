import os
from flask import Flask, render_template, request
import fitz  # PyMuPDF
from dotenv import load_dotenv
from openai import OpenAI  # ✅ Import OpenAI client (new SDK)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # ✅ Create OpenAI client

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    pdf_text = ""
    answer = None
    if request.method == "POST":
        file = request.files["pdf_file"]
        if file:
            # Extract text from PDF
            doc = fitz.open(stream=file.read(), filetype="pdf")
            pdf_text = ""
            for page in doc:
                pdf_text += page.get_text()
            
            # Render the page with the extracted PDF text
            return render_template("index.html", pdf_text=pdf_text, uploaded=True)

    return render_template("index.html", pdf_text=pdf_text, uploaded=False)

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    pdf_text = request.form["pdf_text"]

    # Prepare the conversation prompt
    messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions based on a PDF document."},
        {"role": "user", "content": f"Document Content:\n{pdf_text[:8000]}\n\nQuestion: {question}"},
    ]
    
    try:
        # ✅ Use new SDK syntax
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.8,
        )

        answer = response.choices[0].message.content.strip() 
    except Exception as e:
        answer = f"⚠️ Error fetching response: {str(e)}"

    return render_template("index.html", pdf_text=pdf_text, uploaded=True, question=question, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
