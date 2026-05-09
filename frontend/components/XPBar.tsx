"use client";

interface XPBarProps {
  level: number;
  xpInLevel: number;
  xpNeeded: number;
  totalXp: number;
  className?: string;
}

export default function XPBar({ level, xpInLevel, xpNeeded, totalXp, className }: XPBarProps) {
  const pct = Math.min(100, (xpInLevel / xpNeeded) * 100);
  return (
    <div className={`space-y-1 ${className ?? ""}`}>
      <div className="flex justify-between text-xs">
        <span className="text-rpg-gold font-semibold">Lv {level}</span>
        <span className="text-rpg-muted">
          {xpInLevel} / {xpNeeded} XP
        </span>
      </div>
      <div className="h-2 bg-rpg-bg rounded-full border border-rpg-border overflow-hidden">
        <div
          className="h-full bg-rpg-gold rounded-full transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="text-right text-xs text-rpg-muted">{totalXp.toLocaleString()} total XP</div>
    </div>
  );
}
