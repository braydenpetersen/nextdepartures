import type { NextApiRequest, NextApiResponse } from 'next';

const BACKEND_API_URL = process.env.BACKEND_API_URL as string;
const API_KEY = process.env.API_KEY as string;
const ALLOWED_ORIGINS = ['https://transit.braydenpetersen.com', 'http://localhost:3000'];

if (!BACKEND_API_URL) {
    throw new Error('BACKEND_API_URL is not set');
}

if (!API_KEY) {
    throw new Error('API_KEY is not set');
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    // Check origin
    const origin = req.headers.origin;
    const referer = req.headers.referer;
    
    // In production, ensure request is coming from our site
    if (process.env.NODE_ENV === 'production') {
        if (!origin && !referer) {
            return res.status(403).json({ error: 'Direct API access not allowed' });
        }
        
        const isAllowedOrigin = ALLOWED_ORIGINS.some(allowed => 
            origin === allowed || referer?.startsWith(allowed)
        );
        
        if (!isAllowedOrigin) {
            return res.status(403).json({ error: 'Unauthorized origin' });
        }
    }

    // Only allow GET requests
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { stopCode = '02799' } = req.query;

    // Validate stopCode if needed
    if (typeof stopCode !== 'string') {
        return res.status(400).json({ error: 'Invalid stopCode parameter' });
    }

    try {
        const response = await fetch(`${BACKEND_API_URL}/api/departures?stopCode=${stopCode}`, {
            method: 'GET',
            headers: {
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            console.error('Backend API error:', {
                status: response.status,
                statusText: response.statusText,
                data: errorData
            });
            
            if (response.status === 401) {
                return res.status(500).json({ error: 'Backend authentication failed' });
            }
            
            return res.status(500).json({ error: 'Failed to fetch data from backend' });
        }

        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        console.error('Error fetching departures:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}