import io

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None


def extract_text(uploaded_file):
    filename = uploaded_file.name.lower()
    data = uploaded_file.read()

    # PDF Processing
    if filename.endswith(".pdf"):
        if pdfplumber is None:
            return None, "pdfplumber is not installed."
        try:
            text = []
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return "\n".join(text).strip(), None
        except Exception as e:
            return None, str(e)

    # DOCX Processing
    if filename.endswith(".docx"):
        if docx is None:
            return None, "python-docx is not installed."
        try:
            document = docx.Document(io.BytesIO(data))
            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            )
            return text.strip(), None
        except Exception as e:
            return None, str(e)

    # Plain Text Processing
    if filename.endswith(".txt"):
        return data.decode("utf-8", errors="ignore").strip(), None

    return None, "Please upload a PDF, DOCX, or TXT file."