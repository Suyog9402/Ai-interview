import localFont from "next/font/local";
import { headers } from "next/headers";
import { getAppConfig } from "@/lib/utils";
import { Providers } from "@/components/providers";
import "./globals.css";

// Offline-safe font variable to prevent remote Google Fonts fetch failures during CI/offline builds
const publicSans = {
  variable: "--font-public-sans",
};

const commitMono = localFont({
  src: [
    {
      path: "./fonts/CommitMono-400-Regular.otf",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/CommitMono-700-Regular.otf",
      weight: "700",
      style: "normal",
    },
    {
      path: "./fonts/CommitMono-400-Italic.otf",
      weight: "400",
      style: "italic",
    },
    {
      path: "./fonts/CommitMono-700-Italic.otf",
      weight: "700",
      style: "italic",
    },
  ],
  variable: "--font-commit-mono",
});

interface RootLayoutProps {
  children: React.ReactNode;
}

export default async function RootLayout({ children }: RootLayoutProps) {
  const hdrs = await headers();
  const { accent, accentDark, pageDescription } = await getAppConfig(hdrs);

  const styles = [
    accent ? `:root { --primary: ${accent}; }` : "",
    accentDark ? `.dark { --primary: ${accentDark}; }` : "",
  ]
    .filter(Boolean)
    .join("\n");

  return (
    <html lang="en" className="light" suppressHydrationWarning>
      <head>
        {styles && <style>{styles}</style>}
        <meta name="description" content={pageDescription} />
      </head>
      <body
        className={`${publicSans.variable} ${commitMono.variable} overflow-x-hidden antialiased`}
        suppressHydrationWarning
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
