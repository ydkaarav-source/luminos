import type { Metadata } from "next";
import { Inter, Space_Grotesk, Fraunces } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space-grotesk" });
const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});

export const metadata: Metadata = {
  title: "LuminOS — The AI Operating System for Entrepreneurs",
  description:
    "Go from business idea to daily execution with an AI CEO assistant built for solopreneurs.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable} ${fraunces.variable}`}>
      <body className="min-h-screen bg-grid-fade">{children}</body>
    </html>
  );
}