import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from collections import Counter
import os

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

def words(text):
    return re.findall(r'\w+', text.lower())

def correction(word):
    return max(candidates(word), key=P)

def candidates(word):
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words):
    return set(w for w in words if trie.search(w))

def P(word, N=None):
    global WORDS
    if N is None:
        N = sum(WORDS.values())
    return WORDS[word] / N if word in WORDS else 0

def edits1(word):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def spell_correct():
    input_word = entry.get().strip()
    if not input_word:
        messagebox.showwarning("Warning", "Please enter a word.")
        return

    try:
        corrected_word = correction(input_word)
        if corrected_word == input_word:
            result_var.set(f"No correction found for '{input_word}'.")
        else:
            entry.delete(0, tk.END)
            entry.insert(0, corrected_word)
            result_var.set(f"Corrected word: {corrected_word}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def load_corpus():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not file_path:
        return

    global corpus_file, trie, WORDS
    corpus_file = file_path
    try:
        with open(corpus_file) as f:
            for line in f:
                for word in words(line):
                    trie.insert(word)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the text corpus: {str(e)}")
        return

    WORDS = Counter(words(open(corpus_file).read()))
    messagebox.showinfo("Success", f"Text corpus loaded successfully from '{corpus_file}'.")

def clear_entry():
    entry.delete(0, tk.END)

def provide_recommendations(event=None):
    input_word = entry.get().strip()
    if not input_word:
        result_var.set("")
        return

    recommendations = candidates(input_word)
    if input_word in recommendations:
        recommendations.remove(input_word)  # Remove the input word from recommendations
    if recommendations:
        result_var.set(f"Recommendations: {', '.join(recommendations)}")
    else:
        result_var.set("No recommendations found.")

    # If there's only one recommendation and it's different from the input word, auto-complete the entry field with it
    if len(recommendations) == 1 and recommendations[0] != input_word:
        entry.delete(0, tk.END)
        entry.insert(0, recommendations[0])

root = tk.Tk()
root.title("Spelling Correction and Word Recommendations")

# Set lighter shade of color for the background
bg_color = '#f0f0f0'
root.configure(bg=bg_color)

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the center position
x = (screen_width - 600) / 2
y = (screen_height - 400) / 2

# Set the window position and size
root.geometry("600x400+%d+%d" % (x, y))

frame = ttk.Frame(root, padding="50", style='My.TFrame')
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

label = ttk.Label(frame, text="Enter a word:", font=('Arial', 14), background=bg_color)
label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

entry = ttk.Entry(frame, width=50, font=('Arial', 14))
entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

correct_button = ttk.Button(frame, text="Correct Spelling", command=spell_correct, style='Bold.TButton')
correct_button.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

result_var = tk.StringVar()
result_label = ttk.Label(frame, textvariable=result_var, wraplength=500, font=('Arial', 14), background=bg_color)
result_label.grid(row=3, column=0, pady=(0, 20))

load_button = ttk.Button(frame, text="Add File", command=load_corpus, style='Bold.TButton')
load_button.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

clear_button = ttk.Button(frame, text="Clear Entry", command=clear_entry, style='Bold.TButton')
clear_button.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

# Load the default text corpus file
corpus_file = 'bigdata.txt'
if not os.path.exists(corpus_file):
    messagebox.showerror("Error", f"Default text corpus file '{corpus_file}' not found.")
    root.destroy()
    exit()

# Initialize Trie and WORDS
trie = Trie()
try:
    with open(corpus_file) as f:
        for line in f:
            for word in words(line):
                trie.insert(word)
except Exception as e:
    messagebox.showerror("Error", f"An error occurred while reading the text corpus: {str(e)}")
    root.destroy()
    exit()

WORDS = Counter(words(open(corpus_file).read()))

s = ttk.Style()
s.configure('Bold.TButton', font=('Arial', 14, 'bold'))
s.configure('My.TFrame', background=bg_color)

entry.bind('<KeyRelease>', provide_recommendations)

root.mainloop()
