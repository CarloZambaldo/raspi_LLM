#!/usr/bin/env -S python3

import os
from flask import Flask, request, jsonify, render_template
from llama_cpp import Llama
from datetime import datetime

# === Configurazioni globali ===
LOG_FILE = "chat_log.txt"
MODEL_DIR = "models/"
AVAILABLE_MODELS = []
llm = None
CHAT_HISTORY = {}  # Chiave: IP, Valore: lista dei turni della chat

app = Flask(__name__)

# === Caricamento dei modelli disponibili ===
def load_models():
		global AVAILABLE_MODELS
		if not os.path.exists(MODEL_DIR):
				print("❌ La cartella 'models/' non esiste!")
				AVAILABLE_MODELS = []
				return

		AVAILABLE_MODELS = [f for f in os.listdir(MODEL_DIR) if f.endswith(".gguf")]
		if AVAILABLE_MODELS:
				print("✅ Modelli trovati:", AVAILABLE_MODELS)
		else:
				print("❌ Nessun modello trovato!")

# === Logging conversazione ===
def log_interaction(user_ip, model, question, answer):
		timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		with open(LOG_FILE, "a", encoding="utf-8") as f:
				f.write(f"[{timestamp}] Model: {model}\n")
				f.write(f"User IP: {user_ip}\n")
				f.write(f"Q: {question}\n")
				f.write(f"A: {answer}\n\n======================\n\n")

# === Rotte Flask ===
@app.route("/")
def index():
		return render_template("index.html")

@app.route("/models")
def get_models():
		return jsonify(AVAILABLE_MODELS)

@app.route("/ask", methods=["POST"])
def ask():
		global llm
		ip_address = request.remote_addr
		data = request.get_json()
		question = data.get("question", "").strip()
		model_name = data.get("model", "").strip()

		if not question:
				return jsonify(answer="❌ Please enter a question."), 400
		if not model_name or model_name not in AVAILABLE_MODELS:
				return jsonify(answer="❌ Invalid or missing model."), 400
		if llm is None:
				return jsonify(answer="❌ Model not loaded."), 500

		# Costruzione della cronologia
		chat = CHAT_HISTORY.get(ip_address, [])
		chat.append(f"<start_of_turn>user: {question} <end_of_turn>")
		prompt = "\n".join(chat) + "\n<start_of_turn>model:"

		try:
				print("================================")
				print("IP:", ip_address)
				print("Domanda:", question)

				output = llm(prompt, max_tokens=512)
				answer = output["choices"][0]["text"].strip()

				print("Risposta:", answer)
				chat.append(f"<start_of_turn>model: {answer} <end_of_turn>")
				CHAT_HISTORY[ip_address] = chat
				log_interaction(ip_address, model_name, question, answer)
				print("================================")

				return jsonify(answer=answer)

		except Exception as e:
				print("Errore:", e)
				return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset_chat():
		ip_address = request.remote_addr
		if ip_address in CHAT_HISTORY:
				del CHAT_HISTORY[ip_address]
		return jsonify({"message": "✅ Chat reset successful."})

# === Avvio dell'app ===
if __name__ == "__main__":
		load_models()
		if AVAILABLE_MODELS:
				model_path = os.path.join(MODEL_DIR, AVAILABLE_MODELS[0])
				print(f"🚀 Caricamento modello: {model_path}")
				llm = Llama(
						model_path=model_path,
						n_ctx=2048,
						n_threads=os.cpu_count()
				)
		else:
				print("❌ Nessun modello disponibile. Chiudo.")
				exit(1)

		app.run(host="0.0.0.0", port=8000, debug=True)
