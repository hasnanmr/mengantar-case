# RAG Evaluation

This project uses the `ragas` library to quantitatively evaluate the Retrieval-Augmented Generation (RAG) pipeline.

## Metrics

We currently evaluate the following metrics natively:
- **Faithfulness**: Measures whether the generated answer is entirely derived from the retrieved context. This helps catch LLM hallucinations.
- **Answer Relevancy**: Measures how directly the generated answer addresses the user's initial question.

## Running the Evaluation

1. Make sure `ragas` is installed in your backend environment:
   ```bash
   pip install ragas[spacy]
   ```
2. Navigate to the `backend` directory.
3. Run the evaluation script:
   ```bash
   uv run python scripts/eval_rag.py
   ```

## Test Cases

The evaluation script relies on a predefined set of test cases stored in `backend/tests/rag_test_cases.json`. Each test case should include a `question` and an expected `reference` string.
