

import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv
import pygame
import threading
import os

# LOAD API KEY
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key) if api_key else None

# INITIALIZE AUDIO
pygame.mixer.init()

history = []

# =========================
# TEXT TO SPEECH
# =========================

def speak():

    text = text_box.get("1.0", tk.END).strip()

    if not text:
        messagebox.showwarning("Warning", "Write something first!")
        return

    language = language_var.get()

    def convert():

        try:
            root.after(0, lambda: status.config(text="Generating voice..."))

            tts = gTTS(text=text, lang=language)
            tts.save("speech.mp3")

            pygame.mixer.music.load("speech.mp3")
            pygame.mixer.music.play()

            root.after(0, lambda: status.config(text="Speaking..."))

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            root.after(0, lambda: status.config(text="Finished!"))

        except Exception as e:
            root.after(
                0,
                lambda: messagebox.showerror("Error", str(e))
            )

    threading.Thread(target=convert, daemon=True).start()


def stop_speech():

    pygame.mixer.music.stop()
    status.config(text="Speech stopped!")


def clear_text():

    text_box.delete("1.0", tk.END)
    status.config(text="Text cleared!")


# =========================
# AI CHAT ASSISTANT
# =========================

def add_message(sender, message):

    chat_display.config(state="normal")

    chat_display.insert(
        tk.END,
        sender + ": " + message + "\n\n"
    )

    chat_display.config(state="disabled")
    chat_display.see(tk.END)


def send_message():

    user_text = chat_input.get().strip()

    if not user_text:
        return

    if client is None:
        messagebox.showerror(
            "API Error",
            "Add your GROQ_API_KEY inside the .env file!"
        )
        return

    chat_input.delete(0, tk.END)

    add_message("YOU", user_text)

    history.append({
        "role": "user",
        "content": user_text
    })

    send_button.config(state="disabled")

    def get_response():

        try:

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. "
                                   "Help the user with Python, programming "
                                   "and general questions."
                    }
                ] + history
            )

            answer = response.choices[0].message.content

            history.append({
                "role": "assistant",
                "content": answer
            })

            root.after(
                0,
                lambda: add_message("AI", answer)
            )

        except Exception as e:

            root.after(
                0,
                lambda: add_message("ERROR", str(e))
            )

        finally:

            root.after(
                0,
                lambda: send_button.config(state="normal")
            )

    threading.Thread(target=get_response, daemon=True).start()


def enter_pressed(event):

    send_message()
    return "break"


# =========================
# MAIN WINDOW
# =========================

root = tk.Tk()

root.title("AI TEXT TO SPEECH")
root.geometry("850x850")
root.configure(bg="#101827")

# TITLE

title = tk.Label(
    root,
    text="AI TEXT TO SPEECH",
    font=("Arial", 25, "bold"),
    bg="#101827",
    fg="#38bdf8"
)

title.pack(pady=15)

subtitle = tk.Label(
    root,
    text="Write your text and let AI speak!",
    font=("Arial", 12),
    bg="#101827",
    fg="white"
)

subtitle.pack()

# TEXT BOX

text_box = tk.Text(
    root,
    height=7,
    width=75,
    font=("Arial", 12),
    bg="#1e293b",
    fg="white",
    insertbackground="white",
    relief="flat",
    padx=10,
    pady=10
)

text_box.pack(padx=20, pady=15)

text_box.insert(
    "1.0",
    "Hello! Welcome to my AI Text To Speech application."
)

# LANGUAGE

language_var = tk.StringVar(value="en")

language_menu = tk.OptionMenu(
    root,
    language_var,
    "en",
    "sq",
    "de",
    "fr"
)

language_menu.config(
    bg="#334155",
    fg="white",
    width=15
)

language_menu.pack(pady=5)

# BUTTONS

button_frame = tk.Frame(
    root,
    bg="#101827"
)

button_frame.pack(pady=10)

speak_button = tk.Button(
    button_frame,
    text="SPEAK",
    command=speak,
    bg="#0284c7",
    fg="white",
    font=("Arial", 12, "bold"),
    width=13
)

speak_button.grid(row=0, column=0, padx=5)

stop_button = tk.Button(
    button_frame,
    text="STOP",
    command=stop_speech,
    bg="#dc2626",
    fg="white",
    font=("Arial", 12, "bold"),
    width=13
)

stop_button.grid(row=0, column=1, padx=5)

clear_button = tk.Button(
    button_frame,
    text="CLEAR",
    command=clear_text,
    bg="#475569",
    fg="white",
    font=("Arial", 12, "bold"),
    width=13
)

clear_button.grid(row=0, column=2, padx=5)

status = tk.Label(
    root,
    text="ONLINE",
    font=("Arial", 11, "bold"),
    bg="#101827",
    fg="#22c55e"
)

status.pack(pady=8)

# =========================
# CHATGPT ASSISTANT
# =========================

chat_title = tk.Label(
    root,
    text="AI CHAT ASSISTANT",
    font=("Arial", 19, "bold"),
    bg="#101827",
    fg="#38bdf8"
)

chat_title.pack(pady=10)

chat_display = tk.Text(
    root,
    height=12,
    width=75,
    font=("Arial", 11),
    bg="#1e293b",
    fg="white",
    relief="flat",
    padx=10,
    pady=10,
    wrap="word",
    state="disabled"
)

chat_display.pack(padx=20, pady=5)

add_message(
    "AI",
    "Hello! I am your AI assistant. Ask me anything!"
)

# CHAT INPUT

chat_frame = tk.Frame(
    root,
    bg="#101827"
)

chat_frame.pack(fill="x", padx=20, pady=10)

chat_input = tk.Entry(
    chat_frame,
    font=("Arial", 12),
    bg="#334155",
    fg="white",
    insertbackground="white",
    relief="flat"
)

chat_input.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=10,
    padx=5
)

chat_input.bind("<Return>", enter_pressed)

send_button = tk.Button(
    chat_frame,
    text="SEND",
    command=send_message,
    bg="#0284c7",
    fg="white",
    font=("Arial", 11, "bold"),
    width=12
)

send_button.pack(side="right")

# FOOTER

footer = tk.Label(
    root,
    text="AI TEXT TO SPEECH | POWERED BY PYTHON",
    font=("Arial", 9),
    bg="#101827",
    fg="#64748b"
)

footer.pack(pady=10)

root.mainloop()
