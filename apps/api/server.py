from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import subprocess
import os
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from PyPDF2 import PdfReader
from transformers import T5Tokenizer, T5ForConditionalGeneration
import re

# Charger le modèle T5 et le tokenizer
model_name = "t5-small"  # Utiliser un modèle adapté à la génération de texte
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

app = Flask(__name__)
CORS(app)

all_questions = {}

# Path to the single PDF file
pdf_file_path = "pdf-file.pdf"

# Fonction pour extraire le texte d'un PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def clean_text(text):
    # Retirer les numéros de page, dates, et autres éléments indésirables
    text = re.sub(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', '', text)  # Enlève les dates
    text = re.sub(r'\n+', ' ', text)  # Remplacer les nouvelles lignes par des espaces
    text = re.sub(r'\s+', ' ', text)  # Supprimer les espaces multiples
    text = text.strip()  # Enlever les espaces au début et à la fin
    return text

def generate_questions_from_text(text):
    # Diviser le texte en phrases (ou paragraphes si nécessaire)
    sentences = text.split('.')

    # Liste pour stocker les questions générées
    questions = []

    for sentence in sentences:
        if sentence.strip():  # Vérifie si la phrase n'est pas vide
            # Préparer l'entrée pour T5 (format de l'invite pour générer une question)
            input_text = f"generate question: {sentence.strip()}"
            inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True, padding="longest")

            # Générer la question
            outputs = model.generate(inputs["input_ids"], max_length=50, num_beams=4, early_stopping=True)
            question = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Ajouter la question générée à la liste
            if question and question.strip() not in questions:
                questions.append(question.strip())

    return questions

def clean_and_format_questions(questions):
    formatted_questions = []

    for question in questions:
        # Limite le nombre de mots à 10
        words = question.split()
        if len(words) > 10:
            question = " ".join(words[:10])

        # Vérifie si la question se termine par "?"
        if not question.endswith('?'):
            question += "?"

        formatted_questions.append(question)

    return formatted_questions

@app.route('/date', methods=['GET'])
def get_date():
    # Check if the file exists
    if not os.path.exists(pdf_file_path):
        print(f"❌ Erreur : Le fichier {pdf_file_path} n'existe pas !")
    else:
        # Check if the file is a PDF
        if pdf_file_path.endswith(".pdf"):
            print(f"\n📄 Traitement de : {os.path.basename(pdf_file_path)}")  # Debug

            # Extract and clean the text
            text = extract_text_from_pdf(pdf_file_path)
            cleaned_text = clean_text(text)
            print(f"📝 Texte extrait (500 premiers caractères) : {cleaned_text[:500]}")  # Debug

            if len(cleaned_text) > 10:
                # Generate questions based on the extracted text
                questions = generate_questions_from_text(cleaned_text)
                print(f"❓ Questions générées avant formatage : {questions}")  # Debug

                # Apply the 10-word limit and add "?" if necessary
                formatted_questions = clean_and_format_questions(questions)
                print(f"❓ Questions formatées : {formatted_questions}")  # Debug

                # Store the questions in a dictionary (optional, if you want to keep the structure)
                all_questions = {os.path.basename(pdf_file_path): formatted_questions}
            else:
                print(f"⚠️ {os.path.basename(pdf_file_path)} ne contient pas assez de texte utilisable !")
        else:
            print(f"❌ Erreur : Le fichier {pdf_file_path} n'est pas un PDF !")

    return jsonify({'questions': all_questions})


if __name__ == '__main__':
    app.run()
