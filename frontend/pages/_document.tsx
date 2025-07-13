import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="description" content="Real-time transit departures for University of Waterloo and surrounding areas. Get live departure times for GO Transit and Grand River Transit." />
        
        {/* Open Graph / Facebook - Default meta tags, will be overridden by page-specific ones */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://transit.braydenpetersen.com/" />

        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://transit.braydenpetersen.com/" />

        <link rel="icon" href="/favicon.ico" />
      </Head>
      <body className="antialiased">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
