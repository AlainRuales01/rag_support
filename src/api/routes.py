from flask import Blueprint, jsonify, request

from src.generation.chain import build_rag_chain


api = Blueprint("api", __name__)

FILTER_NAMES = ("category", "brand", "model")


@api.get("/query")
def query_rag():
    question = request.args.get("question", "").strip()
    filters = {
        name: request.args[name].strip()
        for name in FILTER_NAMES
        if request.args.get(name, "").strip()
    }

    if not question:
        return jsonify({"error": "El parámetro 'question' es obligatorio."}), 400

    if not filters:
        return jsonify({
            "error": "Debe enviar al menos uno de: category, brand o model."
        }), 400

    chain = build_rag_chain({"filters": filters})
    response = chain.invoke(question)
    return jsonify({"response": response})