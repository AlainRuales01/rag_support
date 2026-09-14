from src.generation.chain import build_rag_chain
def test_response():
    print("Testing response generation...")
    test_filters = {"category": "impresora", "brand": "EPSON", "model": "L355"}
    question = "¿Cómo puedo saber si el nivel de tinta es bajo en mi impresora L355"
    input_data = {"filters": test_filters}
    chain = build_rag_chain(input_data)
    response = chain.invoke(question)
    print("Response:", response)



if __name__ == "__main__":
    test_response()