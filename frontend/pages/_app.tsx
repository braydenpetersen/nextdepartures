import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { Overpass } from 'next/font/google';
import { useEffect } from 'react';
import '../styles/variables.css';
import { Analytics } from '@vercel/analytics/react';

const overpass = Overpass({
  subsets: ['latin'],
  weight: ['700', '400'],
});

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // Sync blink animation across all elements by calculating a consistent delay
    // based on current time modulo animation duration (1000ms)
    const syncDelay = -(Date.now() % 1000);
    document.documentElement.style.setProperty('--blink-sync-delay', `${syncDelay}ms`);
  }, []);

  return (
    <main className={overpass.className}>
      <Component {...pageProps} />
      <Analytics />
    </main>
  );
}
