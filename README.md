# 🧠 AI-Powered Document Assistant & Quiz Gen

An enterprise-grade NLP agent engineered to digest complex documents, synthesize context, and autonomously generate intelligent assessments.

## ✨ Features

* **Multi-Format Document Processing:** Seamlessly extract text from PDF, Word (`.docx`), and standard text (`.txt`) files.
* **Advanced RAG Architecture:** Utilizes LangChain, FAISS vector stores, and Google's `gemini-embedding-001` model to embed and retrieve document context efficiently.
* **Contextual Q&A:** Ask specific questions about your uploaded documents and get highly accurate answers powered by the `gemini-2.5-flash` model.
* **Automated Quiz Generation:** Dynamically generate interactive, multiple-choice quizzes based on the extracted text. You can customize the number of questions and the difficulty level, complete with automated grading and explanations.

## 📁 Project Structure

* `app.py`: The main Streamlit UI application handling routing, state management, and user interaction.
* `ai_engine.py`: The core backend engine managing text chunking, vector database creation, LangChain prompts, and Google Generative AI API calls.
* `document_processor.py`: Contains the dedicated extraction logic for reading bytes from various document formats using `PyPDF2` and `python-docx`.
* [cite_start]`requirements.txt`: The explicit list of Python dependencies required to run the application, including Streamlit version 1.32.2[cite: 1].
* `sample.txt`: A provided sample text file for quick functional testing.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
