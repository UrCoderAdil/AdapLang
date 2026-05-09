import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AdapLang — Adaptive Language RPG",
  description: "Battle monsters by answering language questions. Powered by IRT adaptive difficulty.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
