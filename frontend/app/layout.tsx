import type { Metadata } from "next";
import { JetBrains_Mono, Nunito } from "next/font/google";
import "./globals.css";
import Nav from "@/components/ui/Nav";
import { I18nProvider } from "@/lib/i18n";

const nunito = Nunito({
  subsets: ["latin"],
  variable: "--font-sans",
  weight: ["400", "500", "600", "700", "800"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "discipliner",
  description: "Discipline and study tracker. No shortcuts.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${nunito.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen bg-background font-sans text-foreground">
        <I18nProvider>
          <Nav />
          <main className="mx-auto max-w-4xl px-4 pb-20 pt-8 sm:px-6">
            {children}
          </main>
        </I18nProvider>
      </body>
    </html>
  );
}
