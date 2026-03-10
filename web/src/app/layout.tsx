import "./globals.css";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.className}>
      <head>
        <title>LinkSage</title>
        <meta name="description" content="Your digital braintrust for links" />
      </head>
      <body>{children}</body>
    </html>
  );
}