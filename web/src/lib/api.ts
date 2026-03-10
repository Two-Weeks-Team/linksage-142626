export interface Bookmark {
  id: string;
  url: string;
  title: string;
  summary: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

export async function fetchSummaries(url: string): Promise<Bookmark> {
  const res = await fetch(`${API_BASE}/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch summary");
  }
  const data = await res.json();
  return data;
}

export async function fetchTags(url: string): Promise<string[]> {
  const res = await fetch(`${API_BASE}/tag`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch tags");
  }
  const data = await res.json();
  return data.tags;
}

export async function searchBookmarks(
  query: string,
  filters?: Record<string, any>
): Promise<Bookmark[]> {
  const params = new URLSearchParams({ q: query });
  if (filters) {
    Object.entries(filters).forEach(([k, v]) => params.append(k, String(v)));
  }
  const res = await fetch(`${API_BASE}/search?${params.toString()}`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Search failed");
  }
  const data = await res.json();
  return data.results;
}