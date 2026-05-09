"""
LoRA fine-tuning for Mistral-7B on language question generation.

Requirements: transformers, peft, trl, bitsandbytes, datasets, accelerate
Run on a GPU with >= 16 GB VRAM (A10G, A100, RTX 3090+).

Usage:
    python ml/finetune/train_lora.py --dataset data/finetune_dataset.jsonl --output ./mistral-language-rpg-lora
"""
import argparse
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"


def load_dataset_from_jsonl(path: str):
    from datasets import Dataset  # type: ignore

    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return Dataset.from_list(records)


def train(dataset_path: str, output_dir: str, num_epochs: int = 3):
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig  # type: ignore
        from peft import LoraConfig, get_peft_model, TaskType  # type: ignore
        from trl import SFTTrainer, SFTConfig  # type: ignore
    except ImportError as e:
        logger.error("Missing dependency: %s\nInstall: pip install transformers peft trl bitsandbytes datasets accelerate", e)
        return

    logger.info("Loading base model: %s", BASE_MODEL)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_dataset_from_jsonl(dataset_path)
    logger.info("Dataset size: %d examples", len(dataset))

    def format_messages(example):
        msgs = example["messages"]
        text = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
        return {"text": text}

    dataset = dataset.map(format_messages)

    training_args = SFTConfig(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        warmup_ratio=0.05,
        lr_scheduler_type="cosine",
        fp16=False,
        bf16=True,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        max_seq_length=512,
        dataset_text_field="text",
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        args=training_args,
    )

    logger.info("Starting training...")
    trainer.train()
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info("Saved fine-tuned model to %s", output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", default="./mistral-language-rpg-lora")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()
    train(args.dataset, args.output, args.epochs)
