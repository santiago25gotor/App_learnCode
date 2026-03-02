import { CONFIG } from '../configuration/config.js';

export async function getVideosRequest() {
    const response = await fetch(CONFIG.WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'getVideos' })
    });
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
}

export async function searchVideoRequest(query) {
    const response = await fetch(CONFIG.WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ searchQuery: query.trim() })
    });
    if (!response.ok) throw new Error(`Error: ${response.status}`);
    return await response.json();
}