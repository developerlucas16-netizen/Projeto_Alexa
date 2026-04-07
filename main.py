import webbrowser
import os
from datetime import datetime
import threading
import tkinter as tk
import re
import unicodedata

# ======================
# IA OFFLINE + VOZ EM TODAS RESPOSTAS
# ======================
WAKE_WORD = "visao cria"
ouvindo_ativo = False

# ===== UTIL =====
def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto

# MAPA DE APPS
APPS = {
    "calculadora": "calc",
    "bloco de notas": "notepad",
    "chrome": "start chrome",
    "explorador": "explorer",
    "spotify": "start spotify",
}

# SITES
SITES = {
    "youtube": "https://www.youtube.com",
    "netflix": "https://www.netflix.com",
    "google": "https://www.google.com",
}

# ===== VOZ =====
try:
    import pyttsx3
    engine = pyttsx3.init()
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False


def falar(texto):
    if not texto:
        return

    print("FALANDO:", texto)

    if TTS_AVAILABLE:
        try:
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print("Erro TTS:", e)

# ===== EXTRAÇÃO =====
def extrair_app_ou_site(texto: str):
    for nome in list(SITES.keys()) + list(APPS.keys()):
        if nome in texto:
            return nome
    return None

# ===== INTENÇÃO =====
def intencao(texto: str):
    t = normalizar(texto)

    if "hora" in t:
        return "hora", None

    if "data" in t or "hoje" in t:
        return "data", None

    if any(v in t for v in ["abrir", "abre", "quero", "assistir"]):
        alvo = extrair_app_ou_site(t)
        if alvo:
            return "abrir", alvo

    if "funk" in t:
        return "musica", "funk"

    if "sertanejo" in t:
        return "musica", "sertanejo"

    if "forro" in t:
        return "musica", "forro"

    if "rock" in t:
        return "musica", "rock"

    if "pesquisar" in t or "buscar" in t:
        termo = re.sub(r"(pesquisar|buscar)", "", t).strip()
        return "pesquisar", termo

    return "desconhecido", None

# ===== EXECUÇÃO =====
def executar_intencao(tipo, dado):
    if tipo == "hora":
        return datetime.now().strftime("Agora são %H:%M")

    if tipo == "data":
        return datetime.now().strftime("Hoje é %d/%m/%Y")

    if tipo == "abrir":
        if dado in SITES:
            webbrowser.open(SITES[dado])
            return f"Abrindo {dado}"

        if dado in APPS:
            os.system(APPS[dado])
            return f"Abrindo {dado}"

        try:
            os.system(f"start {dado}")
            return f"Tentando abrir {dado}"
        except:
            return "Não reconheci o aplicativo"

    if tipo == "musica":
        links = {
            "funk": "https://www.youtube.com/watch?v=fXQj5TarYkc",
            "sertanejo": "https://www.youtube.com/watch?v=kdXWS9KPvmQ",
            "forro": "https://www.youtube.com/watch?v=FvNmjVQwE0o",
            "rock": "https://www.youtube.com/watch?v=iywaBOMvYLI",
        }
        webbrowser.open(links[dado])
        return f"Tocando {dado}"

    if tipo == "pesquisar":
        if not dado:
            return "O que você quer pesquisar?"
        webbrowser.open(f"https://www.google.com/search?q={dado}")
        return f"Pesquisando {dado}"

    return "Não entendi"

# ===== RESPOSTA =====
def responder(texto):
    global ouvindo_ativo
    t = normalizar(texto)

    if "visao" in t and "cria" in t:
        ouvindo_ativo = True
        return "Pode falar"

    if not ouvindo_ativo:
        return None

    tipo, dado = intencao(t)
    resposta = executar_intencao(tipo, dado)

    ouvindo_ativo = False  # volta a dormir

    return resposta

# ===== VOZ =====
try:
    import speech_recognition as sr
    r = sr.Recognizer()
    SPEECH_AVAILABLE = True
except:
    SPEECH_AVAILABLE = False

# ===== LOOP =====
def loop_voz():
    if not SPEECH_AVAILABLE:
        print("Microfone não disponível")
        return

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)

        while True:
            try:
                audio = r.listen(source, phrase_time_limit=5)
                texto = r.recognize_google(audio, language="pt-BR").lower()

                print("Reconhecido:", texto)

                janela.after(0, lambda t=texto: resultado_label.config(text=f"Você disse: {t}"))

                resposta = responder(texto)

                if resposta:
                    janela.after(0, lambda r=resposta: resultado_label.config(text=r))
                    falar(resposta)  # 🔥 SEMPRE FALA

            except Exception as e:
                print("ERRO:", e)

# ===== UI =====
janela = tk.Tk()
janela.title("Cria IA FINAL")
janela.geometry("420x400")
janela.configure(bg="#1e1e1e")

# Título
tk.Label(janela, text="🤖 Cria IA", font=("Arial", 18, "bold"), fg="white", bg="#1e1e1e").pack(pady=15)

# Status
status_label = tk.Label(janela, text="Diga: visao cria", fg="#00ffcc", bg="#1e1e1e")
status_label.pack()

# Resultado
resultado_label = tk.Label(janela, text="...", wraplength=350, fg="white", bg="#1e1e1e")
resultado_label.pack(pady=20)

threading.Thread(target=loop_voz, daemon=True).start()

janela.mainloop()
