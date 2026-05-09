"""
Evaluate fine-tuned model question quality.
Generates N questions per CEFR level and scores them.

Usage:
    python ml/finetune/evaluate.py --model ./mistral-language-rpg-lora --count 20
"""
import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
TEST_SKILL_TAGS = ["greetings", "past_tense", "vocabulary_food", "subjunctive", "articles"]


def generate_from_local_model(model_path: str, language: str, cefr: str, skill_tag: str) -> str | None:
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline  # type: ignore
        import torch

        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path, torch_dtype=torch.bfloat16, device_map="auto"
        )
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

        prompt = (
            f"[INST] Generate a {cefr} {language} question on the skill: {skill_tag}. "
            "Return only valid JSON. [/INST]"
        )
        out = pipe(prompt, max_new_tokens=400, do_sample=False)[0]["generated_text"]
        return out[len(prompt):].strip()
    except Exception as exc:
        logger.error("Generation failed: %s", exc)
        return None


def evaluate(model_path: str, language: str, count: int):
    from backend.quiz_gen.quality_filter import quality_score
    from backend.quiz_gen.schemas import Question

    results = []
    for cefr in CEFR_LEVELS:
        for skill in TEST_SKILL_TAGS[:2]:
            for _ in range(count // (len(CEFR_LEVELS) * 2)):
                raw = generate_from_local_model(model_path, language, cefr, skill)
                if not raw:
                    continue
                try:
                    data = json.loads(raw)
                    q = Question(**data)
                    score_result = quality_score(q)
                    results.append({
                        "cefr": cefr,
                        "skill": skill,
                        "score": score_result.score,
                        "reason": score_result.reason,
                    })
                    logger.info("[%s/%s] Score: %.1f", cefr, skill, score_result.score)
                except Exception as exc:
                    logger.warning("Could not parse output: %s", exc)

    if results:
        avg = sum(r["score"] for r in results) / len(results)
        logger.info("Average quality score: %.2f / 10 across %d questions", avg, len(results))
        print(json.dumps({"average_score": avg, "n": len(results), "results": results}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--language", default="spanish")
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args()
    evaluate(args.model, args.language, args.count)
