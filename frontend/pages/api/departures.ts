import type { NextApiRequest, NextApiResponse } from 'next';

const BACKEND_API_URL = process.env.BACKEND_API_URL as string;
const API_KEY = process.env.API_KEY as string;

if (!BACKEND_API_URL) {
    throw new Error('BACKEND_API_URL is not set');
}

if (!API_KEY) {
    throw new Error('API_KEY is not set');
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    const { stopCode = '02799' } = req.query;

    try {
        const response = await fetch(`${BACKEND_API_URL}/api/departures?stopCode=${stopCode}`, {
            headers: {
                'X-API-Key': API_KEY
            }
        });
        if (!response.ok) {
            return res.status(500).json({ error: 'Failed to fetch data' });
    }

    const data = await response.json();
    res.status(200).json(data); 
  } catch (error) {
    console.error('Error fetching departures:', error);
    res.status(500).json({ error: 'Failed to fetch data' });
  }
}