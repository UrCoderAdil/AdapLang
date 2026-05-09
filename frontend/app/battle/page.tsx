"use client";
import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import BattleArena from "../../components/BattleArena";
import { apiPost, getUserId, getLanguage } from "../../lib/api";

function BattleContent() {
  const router = useRouter();
  const params = useSearchParams();
  const worldId = Number(params.get("world") || "1");

  const [sessionData, setSessionData] = useState<{
    session_id: string;
    question: {id: string; question: string; options: string[]; cefr_level: string; skill_tag: string};
    boss_hp: number;
    player_hp: number;
  } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const userId = getUserId();
    if (!userId) { router.push("/"); return; }

    apiPost<typeof sessionData>("/api/session/start", {
      user_id: userId,
      world_id: worldId,
      language: getLanguage(),
    })
      .then(setSessionData)
      .catch((e) => setError(e.message));
  }, [worldId, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="rpg-border p-8 text-center space-y-4">
          <p className="text-rpg-red">{error}</p>
          <button className="rpg-button-gold" onClick={() => router.push("/map")}>
            Back to Map
          </button>
        </div>
      </div>
    );
  }

  if (!sessionData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="text-4xl animate-float">⚔️</div>
          <p className="text-rpg-muted animate-pulse">Preparing battle…</p>
        </div>
      </div>
    );
  }

  return (
    <BattleArena
      initialQuestion={sessionData.question}
      bossHp={sessionData.boss_hp}
      playerHp={sessionData.player_hp}
      sessionId={sessionData.session_id}
      worldId={worldId}
    />
  );
}

export default function BattlePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-4xl animate-float">⚔️</div>
      </div>
    }>
      <BattleContent />
    </Suspense>
  );
}
