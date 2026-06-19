import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/components/layout/theme-provider";
import { LocaleSync } from "@/components/layout/locale-sync";
import "./globals.css";

/** ChatGPT dùng Söhne (proprietary). Inter + system stack là bản thay thế gần nhất trên web. */
const appFont = Inter({
  variable: "--font-app",
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
  preload: true,
  adjustFontFallback: true,
});

export const metadata: Metadata = {
  title: "",
  description: "AI content creation for Fanpage and Social Media",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={appFont.variable}>
      <body
        className={`${appFont.className} min-h-screen font-sans antialiased bg-white text-neutral-900`}
      >
        <ThemeProvider>
          <LocaleSync />
          {children}
        </ThemeProvider>
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
