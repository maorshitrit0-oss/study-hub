import type { Metadata, Viewport } from "next";
import "katex/dist/katex.min.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Study Hub",
  description: "לומדים מקריאה: הרצאות, תרגולים, שאלונים ומעקב",
  authors: [{ name: "Maor Shitrit" }],
  creator: "Maor Shitrit",
  appleWebApp: { capable: true, title: "Study Hub", statusBarStyle: "black-translucent" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  // Stops iOS from zooming in on a focused field (it left the bottom menu floating mid-screen); pinch zoom still works.
  maximumScale: 1,
  viewportFit: "cover",
  themeColor: "#071a33",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="he" dir="rtl" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
