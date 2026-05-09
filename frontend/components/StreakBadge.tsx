"use client";

interface StreakBadgeProps {
  streak: number;
  className?: string;
}

export default function StreakBadge({ streak, className }: StreakBadgeProps) {
  const fire = streak >= 100 ? "🔥🔥🔥" : streak >= 30 ? "🔥🔥" : streak >= 7 ? "🔥" : "💧";
  const color =
    streak >= 100 ? "border-rpg-gold text-rpg-gold" :
    streak >= 30  ? "border-orange-500 text-orange-400" :
    streak >= 7   ? "border-rpg-red text-rpg-red" :
                    "border-rpg-border text-rpg-muted";

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-sm font-semibold ${color} ${className ?? ""}`}
    >
      <span>{fire}</span>
      <span>{streak} day{streak !== 1 ? "s" : ""}</span>
    </div>
  );
}
