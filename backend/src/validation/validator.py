import os
import logging
import sys
import re
from typing import List, Dict

from src.config.settings import Settings, ensure_directories_exist
from src.rag.system import initialize_rag_system


_word_re = re.compile(r"\w+")


def _tokenize(text: str):
    return [t.lower() for t in _word_re.findall(text or "")]


def jaccard_similarity(a: str, b: str) -> float:
    ta, tb = set(_tokenize(a)), set(_tokenize(b))
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def containment_ratio(expected: str, actual: str) -> float:
    te, ta = set(_tokenize(expected)), set(_tokenize(actual))
    if not te:
        return 0.0
    inter = len(te & ta)
    return inter / len(te)


def parse_queries_and_answers(file_path: str) -> List[Dict[str, str]]:
    queries_data = []
    current_query = None
    current_answer_lines: List[str] = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('- ') and not line.startswith('- ' * 2):
                if current_query:
                    queries_data.append({"query": current_query, "expected_answer": " ".join(current_answer_lines).strip()})
                current_query = line[2:].strip()
                current_answer_lines = []
            elif line.startswith('- ' * 2):
                current_answer_lines.append(line[4:].strip())
            elif line.startswith('##'):
                if current_query:
                    queries_data.append({"query": current_query, "expected_answer": " ".join(current_answer_lines).strip()})
                current_query = None
                current_answer_lines = []
            elif line and current_answer_lines:
                current_answer_lines.append(line.strip())

        if current_query:
            queries_data.append({"query": current_query, "expected_answer": " ".join(current_answer_lines).strip()})
    return queries_data


def run_validation() -> int:
    settings = Settings()
    ensure_directories_exist(settings)

    log_path = os.path.join(settings.reports_dir, "rag_validation_log.txt")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, mode='w'),
            logging.StreamHandler(sys.stdout),
        ],
    )

    logging.info("--- Starting RAG Validation ---")
    logging.info(f"Queries file: {settings.queries_file}")

    qa_pairs = parse_queries_and_answers(settings.queries_file)
    if not qa_pairs:
        logging.error("No queries found. Check the queries file format.")
        return 1

    logging.info(f"Loaded {len(qa_pairs)} query-answer pairs")

    try:
        qa_chain = initialize_rag_system(settings)
        logging.info("RAG system initialized.")
    except Exception as e:
        logging.error(f"Failed to initialize RAG system: {e}")
        return 2

    PASS_JACCARD = 0.30
    PASS_CONTAINMENT = 0.60

    total = len(qa_pairs)
    passed = 0
    results = []

    for i, qa in enumerate(qa_pairs, start=1):
        query = qa["query"]
        expected = qa["expected_answer"]

        try:
            result = qa_chain.invoke(query)
            answer = result.get("result", "")
        except Exception as e:
            logging.error(f"Error invoking RAG for test {i}: {e}")
            results.append({"index": i, "query": query, "status": "ERROR", "jaccard": 0.0, "containment": 0.0})
            continue

        jac = jaccard_similarity(expected, answer)
        cont = containment_ratio(expected, answer)
        is_pass = (jac >= PASS_JACCARD) or (cont >= PASS_CONTAINMENT)
        status = "PASS" if is_pass else "FAIL"
        if is_pass:
            passed += 1

        results.append({
            "index": i,
            "query": query,
            "status": status,
            "jaccard": jac,
            "containment": cont,
        })

    failed = total - passed - sum(1 for r in results if r["status"] == "ERROR")

    # Summary
    logging.info("\n--- Validation Summary ---")
    logging.info(f"Total: {total}, Passed: {passed}, Failed: {failed}")

    # Detailed report
    logging.info("\n--- Detailed Results ---")
    for r in results:
        logging.info(f"[{r['status']}] #{r['index']}: {r['query']} | Jaccard={r['jaccard']:.2f}, Containment={r['containment']:.2f}")

    passed_ids = ", ".join(str(r["index"]) for r in results if r["status"] == "PASS") or "None"
    failed_ids = ", ".join(str(r["index"]) for r in results if r["status"] == "FAIL") or "None"
    error_ids = ", ".join(str(r["index"]) for r in results if r["status"] == "ERROR") or "None"

    logging.info("\n--- Pass/Fail by Test Case ---")
    logging.info(f"Passed: {passed_ids}")
    logging.info(f"Failed: {failed_ids}")
    logging.info(f"Errors: {error_ids}")

    # Also print to stdout for quick viewing
    print("\n--- Validation Summary ---")
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}")
    print("\n--- Pass/Fail by Test Case ---")
    print(f"Passed: {passed_ids}")
    print(f"Failed: {failed_ids}")
    print(f"Errors: {error_ids}")

    return 0 if passed == total else 3


if __name__ == "__main__":
    raise SystemExit(run_validation())



