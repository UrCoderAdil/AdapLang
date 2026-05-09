"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Trophy, Flame } from "lucide-react";
import { apiGet, getUserId } from "../../lib/api";

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  level: number;
  total_xp: number;
  streak: number;
}

interface LeaderboardData {
  period: string;
  leaderboard: LeaderboardEntry[];
}

const RANK_EMOJI: Record<number, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };

export default function LeaderboardPage() {
  const router = useRouter();
  const [data, setData] = useState<LeaderboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const currentUserId = getUserId();

  useEffect(() => {
    apiGet<LeaderboardData>("/api/game/leaderboard?limit=20")
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen p-6 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <button className="rpg-button-ghost text-sm" onClick={() => router.push("/map")}>
          ← Map
        </button>
        <h1 className="text-2xl font-display text-rpg-gold flex items-center gap-2">
          <Trophy size={24} /> Leaderboard
        </h1>
        <div />
      </div>

      {loading ? (
        <div className="flex justify-center pt-20">
          <div className="text-4xl animate-float">🏆</div>
        </div>
      ) : !data?.leaderboard.length ? (
        <div className="rpg-border p-10 text-center text-rpg-muted">
          No players yet. Be the first!
        </div>
      ) : (
        <div className="space-y-2">
          {data.leaderboard.map((entry) => {
            const isCurrentUser = entry.user_id === currentUserId;
            return (
              <div
                key={entry.user_id}
                className={`rpg-border p-4 flex items-center gap-4 transition-all ${
                  isCurrentUser ? "border-rpg-gold bg-rpg-gold/5" : ""
                }`}
              >
                {/* Rank */}
                <div className="w-10 text-center">
                  {RANK_EMOJI[entry.rank] ? (
                    <span className="text-2xl">{RANK_EMOJI[entry.rank]}</span>
                  ) : (
                    <span className="text-rpg-muted font-mono text-lg">#{entry.rank}</span>
                  )}
                </div>

                {/* Name */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`font-semibold ${isCurrentUser ? "text-rpg-gold" : ""}`}>
                      {entry.display_name}
                    </span>
                    {isCurrentUser && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-rpg-gold/20 text-rpg-gold">
                        You
                      </span>
                    )}
                  </div>
                  <div className="text-rpg-muted text-xs">Level {entry.level}</div>
                </div>

                {/* XP */}
                <div className="text-right">
                  <div className="text-rpg-gold font-semibold">{entry.total_xp.toLocaleString()} XP</div>
                  {entry.streak > 0 && (
                    <div className="text-rpg-muted text-xs flex items-center gap-1 justify-end">
                      <Flame size={10} className="text-rpg-red" />
                      {entry.streak}d
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
