#!/usr/bin/env -S python3

import os
from flask import Flask, request, jsonify, render_template
from llama_cpp import Llama
from datetime import datetime

# TO RUN: sudo -E gunicorn -w 4 -b [::]:80 --timeout 500 app:app

LOG_FILE = "chat_log.txt"

#model_cache = {}  # opzionale se vuoi tenerne uno attivo
app = Flask(__name__)
MODEL_DIR = "models/"  # Directory where models are stored
AVAILABLE_MODELS = []


def log_interaction(user_ip, model, question, answer):
	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	with open(LOG_FILE, "a", encoding="utf-8") as f:
		f.write(f"[{timestamp}] Model: {model}\n")
		f.write(f"User IP: {user_ip}\n")
		f.write(f"Q: {question}\n")
		f.write(f"A: {answer}\n\n======================\n\n")

# === Load models at startup ===
def load_models():
	global AVAILABLE_MODELS
	if not os.path.exists(MODEL_DIR):
		print("❌ La cartella 'models/' non esiste!")
		AVAILABLE_MODELS = []
		return

	# Elenca i file .gguf
	AVAILABLE_MODELS = [
		f for f in os.listdir(MODEL_DIR)
		if f.endswith(".gguf")
	]
	print("✅ Modelli trovati:", AVAILABLE_MODELS)

	# Se non ci sono modelli, mostra un messaggio
	if not AVAILABLE_MODELS:
		print("❌ Nessun modello trovato!")
		return

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/models")
def get_models():
	return jsonify(AVAILABLE_MODELS)

@app.route("/ask", methods=["POST"])
def ask():
	ip_address = request.remote_addr
	data = request.get_json()
	question = data.get("question", "").strip()
	model_name = data.get("model", "").strip()

	if not question:
		return jsonify(answer="❌ Please enter a question."), 400
	if not model_name or model_name not in AVAILABLE_MODELS:
		return jsonify(answer="❌ Invalid or missing model."), 400

	model_path = os.path.join(MODEL_DIR, model_name)
	try:
		# Carica il modello dinamicamente
		llm = Llama(
					model_path=model_path, 	# percorso del modello
					n_ctx=1024,				# contesto massimo
					n_threads=4				# usa 4 core della CPU (opzionale)
				)	

		print("================================")
		print("Asking model:\t", model_name)
		print("Question:\t", question)
		print("The model is processing the request...")

		# Modifica il prompt per questo modello specifico
		question = f"<start_of_turn>user: You are the oracle \n answer to my question: {question} \n be coincise <end_of_turn> <start_of_turn>model:"

		output = llm(question, max_tokens=512, stop=[]) #stop=["</s>"])
		text = output["choices"][0]["text"].strip()
		print("Answer:\t", text)
		log_interaction(ip_address, model_name, question, output)
		print("================================")

		return jsonify(answer=text)

	except Exception as e:
		print("Errore:", e)  # utile per debug su console
		return jsonify({"error": str(e)}), 500



# Carica i modelli all'avvio
load_models()
