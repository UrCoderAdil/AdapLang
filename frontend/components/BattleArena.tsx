"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import QuestionCard, { QuestionData } from "./QuestionCard";
import HealthBar from "./HealthBar";
import XPBar from "./XPBar";
import StreakBadge from "./StreakBadge";
import { apiPost, getUserId } from "../lib/api";

interface BattleArenaProps {
  initialQuestion: QuestionData;
  bossHp: number;
  playerHp: number;
  sessionId: string;
  worldId: number;
}

interface AnswerResult {
  correct: boolean;
  explanation: string;
  battle_result: { target: string; damage: number; crit: boolean };
  xp_gained: number;
  xp_progress: { level: number; xp_in_level: number; xp_needed: number; total_xp: number };
  streak: { streak: number };
  new_theta: number;
  new_achievements: { id: string; name: string; desc: string }[];
  next_question: QuestionData | null;
}

const BOSS_SPRITES: Record<number, string> = {
  1: "🌲",
  2: "🦇",
  3: "🏙️",
  4: "🐉",
  5: "🗼",
};

export default function BattleArena({
  initialQuestion,
  bossHp,
  playerHp: initialPlayerHp,
  sessionId,
  worldId,
}: BattleArenaProps) {
  const router = useRouter();
  const [question, setQuestion] = useState<QuestionData>(initialQuestion);
  const [selected, setSelected] = useState<number | null>(null);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [currentBossHp, setBossHp] = useState(bossHp);
  const [currentPlayerHp, setPlayerHp] = useState(initialPlayerHp);
  const [xpData, setXpData] = useState({ level: 1, xp_in_level: 0, xp_needed: 100, total_xp: 0 });
  const [streak, setStreak] = useState(0);
  const [damageText, setDamageText] = useState<string | null>(null);
  const [achievements, setAchievements] = useState<{ name: string; desc: string }[]>([]);
  const [gameOver, setGameOver] = useState<"win" | "lose" | null>(null);
  const questionStartTime = useRef(Date.now());

  useEffect(() => {
    questionStartTime.current = Date.now();
  }, [question]);

  async function handleSelect(index: number) {
    if (selected !== null) return;
    setSelected(index);
    const userId = getUserId();
    if (!userId) { router.push("/"); return; }

    const elapsed = Date.now() - questionStartTime.current;
    try {
      const data = await apiPost<AnswerResult>("/api/session/answer", {
        session_id: sessionId,
        user_id: userId,
        question_id: question.id,
        selected_index: index,
        response_time_ms: elapsed,
      });

      setResult(data);
      setXpData(data.xp_progress);
      setStreak(data.streak.streak);

      if (data.battle_result.target === "boss") {
        const newBossHp = Math.max(0, currentBossHp - data.battle_result.damage);
        setBossHp(newBossHp);
        setDamageText(data.battle_result.crit ? `⚡ CRIT! -${data.battle_result.damage}` : `-${data.battle_result.damage}`);
        if (newBossHp === 0) { setGameOver("win"); return; }
      } else {
        const newPlayerHp = Math.max(0, currentPlayerHp - data.battle_result.damage);
        setPlayerHp(newPlayerHp);
        setDamageText(`💔 -${data.battle_result.damage}`);
        if (newPlayerHp === 0) { setGameOver("lose"); return; }
      }

      if (data.new_achievements.length > 0) {
        setAchievements(data.new_achievements);
        setTimeout(() => setAchievements([]), 4000);
      }

      setTimeout(() => {
        setDamageText(null);
        if (data.next_question) {
          setQuestion(data.next_question);
          setSelected(null);
          setResult(null);
        } else {
          setGameOver("win");
        }
      }, 2200);
    } catch (err) {
      console.error(err);
      setSelected(null);
    }
  }

  if (gameOver) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="rpg-border p-10 text-center space-y-6 animate-slide-up">
          <div className="text-6xl">{gameOver === "win" ? "🏆" : "💀"}</div>
          <h2 className="text-3xl font-display text-rpg-gold">
            {gameOver === "win" ? "Victory!" : "Defeated!"}
          </h2>
          <p className="text-rpg-muted">
            {gameOver === "win"
              ? "You defeated the boss! Your language skills grow stronger."
              : "The beast was too powerful. Train more and try again!"}
          </p>
          <div className="flex gap-3 justify-center">
            <button className="rpg-button-gold" onClick={() => router.push("/map")}>
              World Map
            </button>
            <button className="rpg-button-ghost" onClick={() => window.location.reload()}>
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top HUD */}
      <div className="rpg-border m-4 p-4 grid grid-cols-3 gap-4 items-center">
        <HealthBar current={currentPlayerHp} max={initialPlayerHp} label="Player HP" color="green" />
        <div className="text-center">
          <div className="text-3xl animate-float">{BOSS_SPRITES[worldId] || "👾"}</div>
          {damageText && (
            <div className="text-rpg-red font-bold text-lg animate-slide-up">{damageText}</div>
          )}
        </div>
        <HealthBar current={currentBossHp} max={bossHp} label="Boss HP" color="red" />
      </div>

      {/* Main content */}
      <div className="flex-1 max-w-2xl mx-auto w-full px-4 space-y-4 pb-6">
        <QuestionCard
          question={question}
          selected={selected}
          correct={result?.correct ?? null}
          correctIndex={selected !== null ? (result?.correct ? selected : null) : null}
          onSelect={handleSelect}
          disabled={selected !== null}
        />

        {result && (
          <div
            className={`rpg-border p-4 animate-slide-up border-l-4 ${
              result.correct ? "border-l-rpg-green" : "border-l-rpg-red"
            }`}
          >
            <p className={`font-semibold mb-1 ${result.correct ? "text-rpg-green" : "text-rpg-red"}`}>
              {result.correct ? "✓ Correct!" : "✗ Incorrect"}
              {result.xp_gained > 0 && (
                <span className="ml-2 text-rpg-gold text-sm">+{result.xp_gained} XP</span>
              )}
            </p>
            <p className="text-rpg-muted text-sm">{result.explanation}</p>
            <p className="text-rpg-muted/60 text-xs mt-1">
              Skill level: θ = {result.new_theta}
            </p>
          </div>
        )}

        {/* Achievements toast */}
        {achievements.map((ach) => (
          <div key={ach.name} className="rpg-border p-4 border-rpg-gold animate-slide-up bg-rpg-gold/5">
            <p className="text-rpg-gold font-semibold">🏅 Achievement Unlocked: {ach.name}</p>
            <p className="text-rpg-muted text-sm">{ach.desc}</p>
          </div>
        ))}
      </div>

      {/* Bottom HUD */}
      <div className="rpg-border m-4 p-4 space-y-3">
        <XPBar {...xpData} />
        <div className="flex justify-between items-center">
          <StreakBadge streak={streak} />
          <button className="rpg-button-ghost text-sm py-1.5" onClick={() => router.push("/map")}>
            ← Retreat
          </button>
        </div>
      </div>
    </div>
  );
}
