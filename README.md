# PDF Notes Assistant

A small Python app that turns your lecture PDFs into study material. Upload slides or notes, pick a chapter (a page range), and get a summary, a quiz, flashcards, answers to your questions, and keyword search across all your PDFs.

It runs locally in your browser using Streamlit and uses the free Google Gemini API, so it costs nothing to run.

<!-- Add a screenshot or demo GIF here, for example: -->
<!-- ![App screenshot](screenshot.png) -->

## Features

- Extracts text from PDFs with PyMuPDF
- Optional OCR (Tesseract) for scanned pages that have no real text
- Summary of any page range with headings, bullet points and key terms
- Multiple choice quiz with instant feedback and explanations
- Flashcards that you can download and import into Anki
- "Ask" tab that answers only from the pages you selected
- Keyword search across every uploaded PDF, showing file name, page number and a snippet

## Files in this repository

| File | Purpose |
| --- | --- |
| `notes_assistant.py` | The whole app (single file) |
| `requirements.txt` | Python packages to install |
| `.gitignore` | Keeps keys, caches and PDFs out of Git |
| `README.md` | This guide |

## Before you start

You need:

1. Python 3.9 or newer
2. A free Gemini API key
3. (Only for scanned PDFs) the Tesseract OCR program

Follow the steps below in order. Each step lists what to do in each situation.

---

## Step 1: Check that Python is installed

Open a terminal.

- On Windows: press the Windows key, type `cmd`, press Enter.
- On Mac: open the Terminal app.
- On Linux: open your terminal.

Run:

```
python --version
```

What the result means:

- If it prints `Python 3.9.x` or higher (for example `Python 3.12.1`), go to Step 2.
- If it prints a version lower than 3.9 (for example `Python 3.7.4`), install a newer Python from https://www.python.org/downloads/ and run the command again.
- If it says `python is not recognized` (Windows) or `command not found` (Mac/Linux), try `python3 --version` or, on Windows, `py --version`.
  - If one of those works, use that word (`python3` or `py`) instead of `python` in every command in this guide.
  - If none works, Python is not installed. Download it from https://www.python.org/downloads/. On Windows, tick **Add Python to PATH** on the first installer screen. Then close and reopen the terminal and try again.

## Step 2: Get the project onto your computer

Pick one:

- If you use Git:
  ```
  git clone https://github.com/YOUR-USERNAME/pdf-notes-assistant.git
  cd pdf-notes-assistant
  ```
- If you do not use Git: on the GitHub page click **Code**, then **Download ZIP**, extract it, and open a terminal inside the extracted folder.

Check you are in the right folder by listing files:

- Windows: `dir`
- Mac/Linux: `ls`

You should see `notes_assistant.py` and `requirements.txt`. If you do not, you are in the wrong folder, so use `cd` to move into the correct one.

## Step 3 (recommended): Create a virtual environment

A virtual environment keeps this project's packages separate from the rest of your computer.

Create it:

```
python -m venv venv
```

Activate it, depending on your system:

- Windows Command Prompt: `venv\Scripts\activate`
- Windows PowerShell: `venv\Scripts\Activate.ps1`
  - If PowerShell says running scripts is disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y`, then activate again. Or just use Command Prompt instead.
- Mac or Linux: `source venv/bin/activate`

When it works, your prompt starts with `(venv)`. If you do not see that, the environment is not active. Repeat the activate command.

You must activate it again every time you open a new terminal for this project. If you skip this step entirely, the app still works, the packages just install globally.

## Step 4: Install the packages

```
pip install -r requirements.txt
```

What the result means:

- If it ends with `Successfully installed ...`, go on.
- If it says `pip is not recognized` or `command not found`, use `python -m pip install -r requirements.txt` instead.
- If it shows a permission error, you are probably installing globally. Go back to Step 3 and use a virtual environment, or add `--user` to the command.
- If a package fails to build, upgrade pip first with `python -m pip install --upgrade pip` and try again.

## Step 5: Get a free Gemini API key

1. Go to https://aistudio.google.com and sign in with a Google account.
2. Click **Get API key**, then **Create API key**.
3. Copy the key. Treat it like a password. Never write it into the code and never commit it to GitHub.

## Step 6: Give the app your key

There are two ways. Use whichever you prefer. The app checks them in this order:

1. If the environment variable `GEMINI_API_KEY` exists, the app uses it and shows no key box.
2. Otherwise it shows a password box in the sidebar and waits for you to paste the key. Nothing runs until a key is entered.

To use method 1, set the variable in the same terminal where you will run the app:

- Windows Command Prompt: `set GEMINI_API_KEY=your-key-here`
- Windows PowerShell: `$env:GEMINI_API_KEY="your-key-here"`
- Mac or Linux: `export GEMINI_API_KEY="your-key-here"`

This lasts only for that terminal window. If you open a new terminal, set it again, or just paste the key in the sidebar.

## Step 7 (optional): Install Tesseract for scanned PDFs

Do this only if your PDFs are scans or photos of pages. If your PDFs have normal selectable text, skip this step.

How to tell: open the PDF and try to highlight a word with your mouse.

- If you can highlight words, it has real text. Skip OCR.
- If you cannot highlight anything, it is a scan. Install Tesseract.

Install it depending on your system:

- Windows: download the installer from the UB Mannheim Tesseract page (search "Tesseract UB Mannheim"), run it, and remember the install folder. The default is `C:\Program Files\Tesseract-OCR\`.
  - Then open `notes_assistant.py`, find the line `# pytesseract.pytesseract.tesseract_cmd = ...`, remove the leading `# `, and make sure the path matches where you installed it.
- Mac: `brew install tesseract`
- Linux (Debian/Ubuntu): `sudo apt install tesseract-ocr`

What happens at runtime:

- If a page has fewer than 20 characters of real text and Tesseract is available, the app reads that page with OCR.
- If a page has enough real text, OCR is skipped, so normal PDFs stay fast.
- If Tesseract is not installed, scanned pages stay empty and the app shows a warning for that PDF.

Handwriting is not read well by Tesseract. It works best on printed text.

## Step 8: Run the app

```
streamlit run notes_assistant.py
```

- If a browser tab opens at `http://localhost:8501`, you are done.
- If no tab opens, copy that address into your browser manually.
- If it says `streamlit is not recognized`, use `python -m streamlit run notes_assistant.py`, or check that your virtual environment is active.
- If port 8501 is busy, Streamlit picks the next one (8502 and so on). Use the address it prints.

To stop the app, click the terminal and press `Ctrl + C`.

---

## How to use the app

1. Paste your API key in the sidebar if the app asks for it.
2. Upload one or more PDFs in the sidebar.
3. Choose the **Document** you want to work on.
4. Set the **Start page** and **End page**. This range is your "chapter". Smaller ranges give faster and more focused results. The end page must be greater than or equal to the start page, otherwise the app shows an error and stops.
5. Use the tabs:
   - **Summary**: click the button to get a structured summary.
   - **Quiz**: choose how many questions, click **Generate quiz**, then pick an option for each question to see if you are right.
   - **Flashcards**: choose how many cards, click **Generate flashcards**, click a card to reveal the answer, then use **Download for Anki (.txt)**.
   - **Ask**: type a question about the selected pages. If the notes do not contain the answer, the model is told to say so.
   - **Search**: type a word. It searches all uploaded PDFs (not just the selected pages) and lists every page that contains it.

### Importing flashcards into Anki

1. Open Anki and choose **File > Import**.
2. Select the downloaded `flashcards.txt`.
3. Set the field separator to **Tab**, so the first column is Front and the second is Back.
4. Click **Import**.

---

## How the program makes decisions

This section explains the conditions inside `notes_assistant.py`, in the order they run.

1. **API key check.** If `GEMINI_API_KEY` is set, use it. Else show the sidebar box. If the box is still empty, show a message and stop.
2. **Upload check.** If no PDF is uploaded, show a message and stop. Otherwise every PDF is read page by page.
3. **Per page extraction.** If a page has enough text, keep it. Elif the page is nearly empty and OCR is available, run OCR on it. Else keep it empty.
4. **Scan warning.** If a whole PDF has almost no text after extraction, show a warning that it may be scanned.
5. **Page range check.** If end page is before start page, show an error and stop. Else continue.
6. **Text limit.** The selected pages are joined and cut to 60,000 characters before being sent to the model, so very large ranges are trimmed.
7. **Quiz and flashcards.** The model is asked to reply with a JSON list. The app finds the list in the reply. If it cannot be read, the list is empty and nothing is shown, so just click generate again.
8. **Quiz answers.** If you picked nothing, show nothing. Elif your pick equals the correct answer, show a green "Correct" message. Else show a red message with the right answer.
9. **API errors.** If the API call fails (bad key, no quota, no internet), the app shows the error text instead of crashing.

---

## Troubleshooting

| Problem | Likely cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'fitz'` (or `streamlit`, `google`) | Packages not installed, or virtual environment not active | Activate the venv and run `pip install -r requirements.txt` |
| App keeps asking for the key | Variable not set in this terminal | Set it again (Step 6) or paste it in the sidebar |
| API error mentioning the key | Key copied wrongly or revoked | Create a new key and paste it again |
| API error mentioning quota or 429 | Free limit reached | Wait and retry, or change `MODEL` near the top of the file to `"gemini-2.5-flash"` |
| API error mentioning model not found | Model name changed | Check the current model names in Google's Gemini docs and edit `MODEL` |
| "has almost no extractable text" warning | PDF is a scan | Install Tesseract (Step 7) |
| `TesseractNotFoundError` or empty scanned pages | Tesseract not installed or path wrong | Reinstall and fix the `tesseract_cmd` path on Windows |
| Quiz or flashcards show nothing | Model reply was not valid JSON | Click generate again, or use fewer questions |
| Slow on big PDFs | OCR and large page ranges take time | Use a smaller page range |

## Privacy note

Selected PDF text is sent to Google's Gemini API to generate results. On the free tier, Google may use submitted content to improve its products, so do not upload private or confidential documents.

## Deploying online (optional)

You can host it free on Streamlit Community Cloud:

1. Push this repo to GitHub.
2. Go to https://share.streamlit.io, connect your repo, and set the main file to `notes_assistant.py`.
3. In the app's **Secrets** settings add `GEMINI_API_KEY = "your-key"`.
4. For OCR support, add a file named `packages.txt` to the repo containing the single line `tesseract-ocr`.

Anyone who uses the public link will use your key's quota, so many people share only the repo and a demo video instead.

## Ideas for improvement

- Save summaries, quizzes and flashcards in a SQLite database
- Let the user choose summary length and quiz difficulty
- Export the summary as a PDF
- Read handwritten notes by sending page images to a vision model

## Tech used

Python, Streamlit, PyMuPDF, Google Gemini API (`google-genai`), Tesseract with `pytesseract` and Pillow

## License

Add a license of your choice (MIT is common for student projects) as a `LICENSE` file.
