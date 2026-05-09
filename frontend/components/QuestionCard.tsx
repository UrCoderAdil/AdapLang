"use client";
import clsx from "clsx";

export interface QuestionData {
  id: string;
  question: string;
  options: string[];
  cefr_level: string;
  skill_tag: string;
}

interface QuestionCardProps {
  question: QuestionData;
  selected: number | null;
  correct: boolean | null;
  correctIndex: number | null;
  onSelect: (index: number) => void;
  disabled?: boolean;
}

export default function QuestionCard({
  question,
  selected,
  correct,
  correctIndex,
  onSelect,
  disabled,
}: QuestionCardProps) {
  function optionClass(idx: number) {
    if (selected === null) {
      return "border-rpg-border hover:border-rpg-gold hover:bg-rpg-gold/5 cursor-pointer";
    }
    if (idx === correctIndex) {
      return "border-rpg-green bg-rpg-green/10 text-rpg-green";
    }
    if (idx === selected && !correct) {
      return "border-rpg-red bg-rpg-red/10 text-rpg-red animate-shake";
    }
    return "border-rpg-border opacity-50";
  }

  return (
    <div className="rpg-border p-6 space-y-6 animate-slide-up">
      <div className="flex items-center gap-2 text-xs text-rpg-muted">
        <span className="px-2 py-0.5 rounded border border-rpg-purple text-rpg-purple">
          {question.cefr_level}
        </span>
        <span>•</span>
        <span>{question.skill_tag.replace(/_/g, " ")}</span>
      </div>

      <p className="text-lg font-medium text-rpg-text">{question.question}</p>

      <div className="space-y-3">
        {question.options.map((option, idx) => (
          <button
            key={idx}
            onClick={() => !disabled && selected === null && onSelect(idx)}
            disabled={disabled || selected !== null}
            className={clsx(
              "w-full text-left px-4 py-3 rounded-lg border transition-all duration-200",
              optionClass(idx)
            )}
          >
            <span className="text-rpg-muted mr-3 font-mono text-sm">
              {["A", "B", "C", "D"][idx]}.
            </span>
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
