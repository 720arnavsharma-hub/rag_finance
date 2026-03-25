from flask import Flask, render_template, request, jsonify
import os

from ingestion import build_vector_store
from retrieval import retrieve_context_multi
from generation import generate_answer, expand_query, clear_history
from validation import is_allowed_file, validate_query

app = Flask(__name__)

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

vector_store = None


def get_uploaded_files():
    files = []
    for f in os.listdir(UPLOAD_FOLDER):
        if os.path.isfile(os.path.join(UPLOAD_FOLDER, f)):
            files.append(f)
    return files


@app.route("/", methods=["GET", "POST"])
def index():
    global vector_store
    answer = ""

    if request.method == "POST":

        if "files" in request.files:
            files = request.files.getlist("files")
            saved = 0

            for file in files:
                if file.filename and is_allowed_file(file.filename):
                    path = os.path.join(UPLOAD_FOLDER, file.filename)
                    file.save(path)
                    saved += 1

            if saved == 0:
                answer = "No valid files uploaded. Only .txt and .pdf allowed."
            else:
                try:
                    vector_store = build_vector_store(UPLOAD_FOLDER)
                    answer = f"{saved} document(s) indexed successfully."
                except Exception as e:
                    answer = f"Indexing error: {str(e)}"

        elif "query" in request.form:
            query = request.form["query"]

            valid, error = validate_query(query)
            if not valid:
                answer = error
            elif vector_store is None:
                try:
                    vector_store = build_vector_store(UPLOAD_FOLDER)
                except:
                    answer = "Please upload documents first."
            
            if not answer:
                try:
                    expanded = expand_query(query)
                    context = retrieve_context_multi(vector_store, expanded)
                    if context:
                        answer = generate_answer(context, query)
                    else:
                        answer = "Not found in document."
                except Exception as e:
                    answer = f"Query error: {str(e)}"

    return render_template("index.html", answer=answer, files=get_uploaded_files())


@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    global vector_store
    path = os.path.join(UPLOAD_FOLDER, filename)
    try:
        if os.path.exists(path):
            os.remove(path)
        remaining = get_uploaded_files()
        if remaining:
            vector_store = build_vector_store(UPLOAD_FOLDER)
        else:
            vector_store = None
        clear_history()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)