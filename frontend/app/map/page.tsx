"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Sword, Star } from "lucide-react";
import { apiGet, getUserId } from "../../lib/api";

interface World {
  id: number;
  name: string;
  topic: string;
  unlock: string;
  difficulty: number;
}

interface UnlockedData {
  unlocked_world_ids: number[];
}

const WORLD_ICONS: Record<number, string> = {
  1: "🌲",
  2: "🦇",
  3: "🏙️",
  4: "🐉",
  5: "🗼",
};

const WORLD_COLORS: Record<number, string> = {
  1: "border-rpg-green",
  2: "border-rpg-blue",
  3: "border-rpg-gold",
  4: "border-rpg-purple",
  5: "border-rpg-red",
};

export default function MapPage() {
  const router = useRouter();
  const [worlds, setWorlds] = useState<World[]>([]);
  const [unlockedIds, setUnlockedIds] = useState<number[]>([1]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userId = getUserId();

    Promise.all([
      apiGet<{ worlds: World[] }>("/api/game/worlds"),
      userId
        ? apiGet<UnlockedData>(`/api/game/worlds/${userId}/unlocked`)
        : Promise.resolve({ unlocked_world_ids: [1] }),
    ])
      .then(([worldData, unlockedData]) => {
        setWorlds(worldData.worlds);
        setUnlockedIds(unlockedData.unlocked_world_ids);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  function enterWorld(worldId: number) {
    router.push(`/battle?world=${worldId}`);
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-4xl animate-float">🗺️</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-display text-rpg-gold">World Map</h1>
          <p className="text-rpg-muted text-sm mt-1">Choose your battle zone</p>
        </div>
        <div className="flex gap-2">
          <button className="rpg-button-ghost text-sm" onClick={() => router.push("/profile")}>
            👤 Profile
          </button>
          <button className="rpg-button-ghost text-sm" onClick={() => router.push("/leaderboard")}>
            🏆 Leaderboard
          </button>
        </div>
      </div>

      {/* World path */}
      <div className="space-y-4">
        {worlds.map((world, idx) => {
          const isUnlocked = unlockedIds.includes(world.id);
          const borderColor = isUnlocked ? WORLD_COLORS[world.id] : "border-rpg-border";

          return (
            <div
              key={world.id}
              className={`rpg-border border-l-4 ${borderColor} p-5 flex items-center justify-between transition-all duration-200 ${
                isUnlocked ? "hover:brightness-110" : "opacity-50"
              } ${isUnlocked ? "cursor-pointer" : "cursor-not-allowed"}`}
              onClick={() => isUnlocked && enterWorld(world.id)}
            >
              <div className="flex items-center gap-4">
                <div className="text-4xl">{WORLD_ICONS[world.id] || "🌍"}</div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="font-display text-lg text-rpg-text">{world.name}</h2>
                    {idx === 0 && (
                      <span className="text-xs px-2 py-0.5 rounded bg-rpg-green/20 text-rpg-green border border-rpg-green/30">
                        DEFAULT
                      </span>
                    )}
                  </div>
                  <p className="text-rpg-muted text-sm">{world.topic}</p>
                  <p className="text-rpg-muted/60 text-xs">
                    Difficulty: {world.difficulty > 0 ? "+" : ""}{world.difficulty.toFixed(1)} (IRT scale)
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {isUnlocked ? (
                  <button
                    className="rpg-button-gold flex items-center gap-2 py-2 px-4"
                    onClick={(e) => { e.stopPropagation(); enterWorld(world.id); }}
                  >
                    <Sword size={16} />
                    Battle
                  </button>
                ) : (
                  <div className="flex items-center gap-2 text-rpg-muted">
                    <Lock size={16} />
                    <span className="text-sm">Locked</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Review button */}
      <div className="mt-8 rpg-border p-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Star className="text-rpg-gold" size={24} />
          <div>
            <h3 className="font-semibold">Daily Review</h3>
            <p className="text-rpg-muted text-sm">Practice words due for spaced repetition</p>
          </div>
        </div>
        <button className="rpg-button-ghost" onClick={() => router.push("/battle?world=0&mode=review")}>
          Review →
        </button>
      </div>
    </div>
  );
}
