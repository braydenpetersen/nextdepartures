import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="description" content="Real-time transit departures for University of Waterloo and surrounding areas. Get live departure times for GO Transit and Grand River Transit." />
        
        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://transit.braydenpetersen.com/" />
        <meta property="og:title" content="Live Departure Board" />
        <meta property="og:description" content="Real-time transit departures for University of Waterloo and surrounding areas" />
        <meta property="og:image" content="https://transit.braydenpetersen.com/og-image.png" />

        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://transit.braydenpetersen.com/" />
        <meta property="twitter:title" content="Live Departure Board" />
        <meta property="twitter:description" content="Real-time transit departures for University of Waterloo and surrounding areas" />
        <meta property="twitter:image" content="https://transit.braydenpetersen.com/og-image.png" />

        <link rel="icon" href="/favicon.ico" />
      </Head>
      <body className="antialiased">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
