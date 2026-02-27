# eval_rag.py
"""RAG Evaluation Script

This script evaluates the Retrieval-Augmented Generation (RAG) pipeline using the
`ragas` library. It measures:
- Faithfulness: how well the generated answer is supported by the retrieved
  context.
- Answer Relevancy: relevance of the answer to the original user query.

The script loads a set of test queries with reference answers, runs the
retrieval and generation steps, and prints a summary report.
"""

import json
from pathlib import Path

# Ensure ragas is installed in the environment.
# pip install ragas[spacy]

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

# Project imports – adjust if the module path differs.
from app.rag.knowledge_base import query_knowledge
from app.core.config import get_settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

settings = get_settings()

def load_test_cases() -> list[dict]:
    """Load test cases from a JSON file.

    Expected format:
    [{"question": "...", "reference": "..."}, ...]
    """
    test_file = Path(__file__).parent.parent / "tests" / "rag_test_cases.json"
    if not test_file.exists():
        raise FileNotFoundError(f"Test cases file not found: {test_file}")
    with open(test_file, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_answer(question: str, context: str) -> str:
    system_prompt = f"You are an AI sales assistant for Acne Care. Use the provided context to answer the user's question. Context:\n{context}\nIf the context is empty, answer based on general product knowledge."
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0.0,
        streaming=False,
    )
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)])
    return response.content

def run_evaluation():
    cases = load_test_cases()
    results = []
    for case in cases:
        q = case["question"]
        ref = case["reference"]
        ctx = query_knowledge(q)
        ans = generate_answer(q, ctx)
        results.append({"question": q, "answer": ans, "reference": ref, "context": ctx})

    df = evaluate(results, metrics=[faithfulness, answer_relevancy])
    print("RAG Evaluation Summary:")
    print(df.mean())

if __name__ == "__main__":
    run_evaluation()
