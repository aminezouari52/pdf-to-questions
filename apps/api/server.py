from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import subprocess
import os
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from PyPDF2 import PdfReader
import re

# Load the T5 model and tokenizer
model_name = "t5-small"  # Use a model suited for text generation
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

app = Flask(__name__)
CORS(app)

all_questions = {}

# Path to the single PDF file
pdf_file_path = "pdf-file.pdf"

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def clean_text(text):
    # Remove page numbers, dates, and other unwanted elements
    text = re.sub(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', '', text)  # Remove dates
    text = re.sub(r'\n+', ' ', text)  # Replace new lines with spaces
    text = re.sub(r'\s+', ' ', text)  # Remove multiple spaces
    text = text.strip()  # Trim spaces at the beginning and end
    return text

def generate_questions_from_text(text):
    # Split text into sentences (or paragraphs if needed)
    sentences = text.split('.')

    # List to store generated questions
    questions = []

    for sentence in sentences:
        if sentence.strip():  # Check if the sentence is not empty
            # Prepare input for T5 (prompt format for question generation)
            input_text = f"generate question: {sentence.strip()}"
            inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True, padding="longest")

            # Generate the question
            outputs = model.generate(inputs["input_ids"], max_length=50, num_beams=4, early_stopping=True)
            question = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Add the generated question to the list
            if question and question.strip() not in questions:
                questions.append(question.strip())

    return questions

def clean_and_format_questions(questions):
    formatted_questions = []

    for question in questions:
        # Limit the number of words to 10
        words = question.split()
        if len(words) > 10:
            question = " ".join(words[:10])

        # Ensure the question ends with "?"
        if not question.endswith('?'):
            question += "?"

        formatted_questions.append(question)

    return formatted_questions

@app.route('/date', methods=['GET'])
def get_date():
    # Check if the file exists
    if not os.path.exists(pdf_file_path):
        print(f"❌ Error: The file {pdf_file_path} does not exist!")
    else:
        # Check if the file is a PDF
        if pdf_file_path.endswith(".pdf"):
            print(f"\n📄 Processing: {os.path.basename(pdf_file_path)}")  # Debug

            # Extract and clean the text
            text = extract_text_from_pdf(pdf_file_path)
            cleaned_text = clean_text(text)
            print(f"📝 Extracted text (first 500 characters): {cleaned_text[:500]}")  # Debug

            if len(cleaned_text) > 10:
                # Generate questions based on the extracted text
                questions = generate_questions_from_text(cleaned_text)
                print(f"❓ Generated questions before formatting: {questions}")  # Debug

                # Apply the 10-word limit and add "?" if necessary
                formatted_questions = clean_and_format_questions(questions)
                print(f"❓ Formatted questions: {formatted_questions}")  # Debug

                # Store the questions in a dictionary (optional, if you want to keep the structure)
                all_questions = {os.path.basename(pdf_file_path): formatted_questions}
            else:
                print(f"⚠️ {os.path.basename(pdf_file_path)} does not contain enough usable text!")
        else:
            print(f"❌ Error: The file {pdf_file_path} is not a PDF!")

    return jsonify({'questions': all_questions})

if __name__ == '__main__':
    app.run()
