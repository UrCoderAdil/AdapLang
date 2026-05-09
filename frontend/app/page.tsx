"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sword, BookOpen, Trophy, Zap } from "lucide-react";

const LANGUAGES = ["Spanish", "French", "German", "Japanese", "Portuguese"];
const CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];

export default function LandingPage() {
  const router = useRouter();
  const [step, setStep] = useState<"landing" | "onboard">("landing");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [language, setLanguage] = useState("Spanish");
  const [cefr, setCefr] = useState("A1");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleStart() {
    if (!name.trim() || !email.trim()) {
      setError("Please enter your name and email.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/user/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          display_name: name,
          starting_cefr: cefr,
          language: language.toLowerCase(),
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Registration failed");
      }
      const user = await res.json();
      localStorage.setItem("user_id", user.id);
      localStorage.setItem("language", language.toLowerCase());
      router.push("/map");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (step === "onboard") {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md rpg-border p-8 space-y-6 animate-slide-up">
          <h2 className="text-2xl font-display text-rpg-gold text-center">
            ⚔️ Create Your Hero
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-rpg-muted mb-1">Hero Name</label>
              <input
                className="w-full bg-rpg-bg border border-rpg-border rounded-lg px-4 py-2 text-rpg-text focus:outline-none focus:border-rpg-gold"
                placeholder="Enter your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm text-rpg-muted mb-1">Email</label>
              <input
                type="email"
                className="w-full bg-rpg-bg border border-rpg-border rounded-lg px-4 py-2 text-rpg-text focus:outline-none focus:border-rpg-gold"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm text-rpg-muted mb-1">Language to Learn</label>
              <div className="grid grid-cols-3 gap-2">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang}
                    onClick={() => setLanguage(lang)}
                    className={`py-2 rounded-lg border text-sm transition-all ${
                      language === lang
                        ? "border-rpg-gold text-rpg-gold bg-rpg-gold/10"
                        : "border-rpg-border text-rpg-muted hover:border-rpg-gold/50"
                    }`}
                  >
                    {lang}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm text-rpg-muted mb-1">
                Current Level (CEFR)
              </label>
              <div className="grid grid-cols-6 gap-1">
                {CEFR_LEVELS.map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setCefr(lvl)}
                    className={`py-2 rounded-lg border text-sm font-mono transition-all ${
                      cefr === lvl
                        ? "border-rpg-purple text-rpg-purple bg-rpg-purple/10"
                        : "border-rpg-border text-rpg-muted hover:border-rpg-purple/50"
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {error && <p className="text-rpg-red text-sm text-center">{error}</p>}

          <button
            onClick={handleStart}
            disabled={loading}
            className="rpg-button-gold w-full disabled:opacity-50"
          >
            {loading ? "Creating hero…" : "Begin Adventure ⚔️"}
          </button>
          <button onClick={() => setStep("landing")} className="rpg-button-ghost w-full">
            ← Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center space-y-12">
      {/* Hero */}
      <div className="space-y-4 animate-slide-up">
        <div className="text-7xl animate-float">⚔️</div>
        <h1 className="text-5xl font-display font-bold text-rpg-gold">AdapLang</h1>
        <p className="text-xl text-rpg-muted max-w-lg">
          Battle monsters by answering language questions. The harder you get, the harder
          the questions. Powered by{" "}
          <span className="text-rpg-purple font-semibold">Item Response Theory</span>.
        </p>
        <button
          onClick={() => setStep("onboard")}
          className="rpg-button-gold text-lg px-10 py-4 animate-pulse-gold"
        >
          Start Your Quest →
        </button>
      </div>

      {/* Feature pills */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl w-full">
        {[
          { icon: <Zap size={20} />, title: "Adaptive IRT", desc: "Questions calibrated to your exact skill" },
          { icon: <Sword size={20} />, title: "RPG Battles", desc: "Defeat bosses with your vocabulary" },
          { icon: <BookOpen size={20} />, title: "Spaced Repetition", desc: "FSRS algorithm keeps knowledge fresh" },
          { icon: <Trophy size={20} />, title: "Leaderboard", desc: "Compete with language learners worldwide" },
        ].map((feat) => (
          <div key={feat.title} className="rpg-border p-4 space-y-2 text-left">
            <div className="text-rpg-gold">{feat.icon}</div>
            <div className="font-semibold text-sm">{feat.title}</div>
            <div className="text-rpg-muted text-xs">{feat.desc}</div>
          </div>
        ))}
      </div>

      {/* Returning user */}
      <button
        onClick={() => router.push("/map")}
        className="text-rpg-muted text-sm hover:text-rpg-gold transition-colors"
      >
        Already have an account? Continue →
      </button>
    </div>
  );
}
