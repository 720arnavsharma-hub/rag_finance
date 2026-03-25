import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Load ONCE when server starts, reuse forever
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        print("[ingestion] Loading embedding model...")
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings


def _load_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def _load_pdf(path):
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except ImportError:
        raise ImportError("pypdf not installed. Run: pip install pypdf")


def build_vector_store(folder):
    documents = []
    supported = {".txt": _load_txt, ".pdf": _load_pdf}

    for filename in os.listdir(folder):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in supported:
            continue
        path = os.path.join(folder, filename)
        try:
            content = supported[ext](path)
        except Exception as e:
            print(f"[ingestion] Skipping {filename}: {e}")
            continue
        if not content:
            continue
        documents.append(Document(
            page_content=content,
            metadata={"source": filename}
        ))

    if not documents:
        raise ValueError("No valid text found in uploaded documents.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("Text split produced no chunks.")

    print(f"[ingestion] {len(documents)} doc(s) → {len(chunks)} chunks")

    vector_store = FAISS.from_documents(chunks, get_embeddings())
    return vector_store