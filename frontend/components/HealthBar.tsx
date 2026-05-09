"use client";
import clsx from "clsx";

interface HealthBarProps {
  current: number;
  max: number;
  label: string;
  color?: "red" | "green" | "blue" | "gold";
  className?: string;
}

const COLOR_MAP: Record<string, string> = {
  red:   "bg-rpg-red",
  green: "bg-rpg-green",
  blue:  "bg-rpg-blue",
  gold:  "bg-rpg-gold",
};

export default function HealthBar({ current, max, label, color = "green", className }: HealthBarProps) {
  const pct = Math.max(0, Math.min(100, (current / max) * 100));
  const barColor = COLOR_MAP[color] ?? "bg-rpg-green";
  const isLow = pct <= 25;

  return (
    <div className={clsx("space-y-1", className)}>
      <div className="flex justify-between text-xs text-rpg-muted">
        <span>{label}</span>
        <span>
          {current} / {max}
        </span>
      </div>
      <div className="h-3 bg-rpg-bg rounded-full border border-rpg-border overflow-hidden">
        <div
          className={clsx(
            "h-full rounded-full transition-all duration-500",
            barColor,
            isLow && "animate-pulse"
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
