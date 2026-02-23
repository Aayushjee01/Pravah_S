import "./globals.css";

export const metadata = {
  title: "Navi Mumbai House Price Predictor | AI-Powered Real Estate Valuation",
  description:
    "Get accurate, AI-powered property price estimates for Navi Mumbai. Covers Kharghar, Panvel, Vashi, Nerul, Airoli, Ulwe, and more. Instant valuations backed by machine learning.",
  keywords: [
    "Navi Mumbai",
    "house price",
    "property valuation",
    "real estate",
    "AI prediction",
    "Kharghar",
    "Panvel",
    "Vashi",
  ],
  openGraph: {
    title: "Navi Mumbai House Price Predictor",
    description:
      "AI-powered property price estimates for Navi Mumbai neighborhoods",
    type: "website",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
