import type { NextApiRequest, NextApiResponse } from 'next';

const BACKEND_API_URL = process.env.BACKEND_API_URL as string;

if (!BACKEND_API_URL) {
    throw new Error('BACKEND_API_URL is not set');
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    // Only allow GET requests
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { station, name } = req.query;

    try {
        const params = new URLSearchParams();
        if (station && typeof station === 'string') {
            params.append('station', station);
        }
        if (name && typeof name === 'string') {
            params.append('name', name);
        }

        const response = await fetch(`${BACKEND_API_URL}/api/og-image?${params}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Backend OG image API error:', {
                status: response.status,
                statusText: response.statusText
            });
            return res.status(500).json({ error: 'Failed to generate image' });
        }

        // Get the image data
        const imageBuffer = await response.arrayBuffer();
        
        // Set proper headers and return the image
        res.setHeader('Content-Type', 'image/png');
        res.setHeader('Cache-Control', 'public, max-age=3600'); // Cache for 1 hour
        res.send(Buffer.from(imageBuffer));

    } catch (error) {
        console.error('Error generating OG image:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
}