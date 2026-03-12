import PyPDF2
from docx import Document

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PyPDF2.PdfReader(pdf)
        for page in pdf_reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

def get_docx_text(docx_docs):
    text = ""
    for doc in docx_docs:
        document = Document(doc)
        for para in document.paragraphs:
            text += para.text + "\n"
    return text

def get_txt_text(txt_docs):
    text = ""
    for txt in txt_docs:
        text += txt.getvalue().decode("utf-8") + "\n"
    return text

def process_documents(file_uploads):
    # Separate files by extension
    pdf_docs = []
    docx_docs = []
    txt_docs = []
    
    for file in file_uploads:
        if file.name.endswith(".pdf"):
            pdf_docs.append(file)
        elif file.name.endswith(".docx"):
            docx_docs.append(file)
        elif file.name.endswith(".txt"):
            txt_docs.append(file)
            
    raw_text = ""
    if pdf_docs:
        raw_text += get_pdf_text(pdf_docs)
    if docx_docs:
        raw_text += get_docx_text(docx_docs)
    if txt_docs:
        raw_text += get_txt_text(txt_docs)
        
    return raw_text
