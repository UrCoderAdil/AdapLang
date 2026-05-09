"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import XPBar from "../../components/XPBar";
import StreakBadge from "../../components/StreakBadge";
import { apiGet, getUserId } from "../../lib/api";

interface ProfileData {
  id: string;
  email: string;
  display_name: string | null;
  streak: number;
  level: number;
  total_xp: number;
  current_world: number;
  achievements: string[];
  skills: Record<string, { theta: number; cefr: string }>;
  xp_progress: { level: number; xp_in_level: number; xp_needed: number; total_xp: number };
  total_questions_answered: number;
  accuracy: number;
}

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const userId = getUserId();
    if (!userId) { router.push("/"); return; }

    apiGet<ProfileData>(`/api/user/${userId}/stats`)
      .then(setProfile)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-4xl animate-float">👤</div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="rpg-border p-8 text-center space-y-4">
          <p className="text-rpg-red">{error || "Profile not found"}</p>
          <button className="rpg-button-gold" onClick={() => router.push("/")}>Home</button>
        </div>
      </div>
    );
  }

  const CEFR_COLOR: Record<string, string> = {
    A1: "text-rpg-muted", A2: "text-rpg-blue",
    B1: "text-rpg-green", B2: "text-rpg-gold",
    C1: "text-rpg-purple", C2: "text-rpg-red",
  };

  return (
    <div className="min-h-screen p-6 max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button className="rpg-button-ghost text-sm" onClick={() => router.push("/map")}>
          ← Map
        </button>
        <h1 className="text-2xl font-display text-rpg-gold">Hero Profile</h1>
        <div />
      </div>

      {/* Identity */}
      <div className="rpg-border p-6 flex items-center gap-5">
        <div className="text-5xl">🧙</div>
        <div>
          <h2 className="text-xl font-semibold">{profile.display_name || "Anonymous Hero"}</h2>
          <p className="text-rpg-muted text-sm">{profile.email}</p>
          <StreakBadge streak={profile.streak} className="mt-2" />
        </div>
      </div>

      {/* XP */}
      <div className="rpg-border p-5">
        <h3 className="text-sm text-rpg-muted mb-3 uppercase tracking-wider">Experience</h3>
        <XPBar {...profile.xp_progress} />
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Questions", value: profile.total_questions_answered.toLocaleString() },
          { label: "Accuracy", value: `${Math.round(profile.accuracy * 100)}%` },
          { label: "World", value: `#${profile.current_world}` },
        ].map((stat) => (
          <div key={stat.label} className="rpg-border p-4 text-center">
            <div className="text-2xl font-bold text-rpg-gold">{stat.value}</div>
            <div className="text-rpg-muted text-xs mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Skill levels */}
      {Object.keys(profile.skills).length > 0 && (
        <div className="rpg-border p-5 space-y-3">
          <h3 className="text-sm text-rpg-muted uppercase tracking-wider">Skill Levels</h3>
          {Object.entries(profile.skills).map(([skill, data]) => (
            <div key={skill} className="flex items-center justify-between">
              <span className="capitalize text-sm">{skill.replace(/_/g, " ")}</span>
              <div className="flex items-center gap-3">
                <div className="text-xs text-rpg-muted">θ = {data.theta.toFixed(2)}</div>
                <span className={`text-sm font-semibold font-mono ${CEFR_COLOR[data.cefr] || ""}`}>
                  {data.cefr}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Achievements */}
      {profile.achievements.length > 0 && (
        <div className="rpg-border p-5 space-y-3">
          <h3 className="text-sm text-rpg-muted uppercase tracking-wider">
            Achievements ({profile.achievements.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {profile.achievements.map((id) => (
              <span
                key={id}
                className="px-3 py-1 rounded-full border border-rpg-gold/30 bg-rpg-gold/5 text-rpg-gold text-xs"
              >
                🏅 {id.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
