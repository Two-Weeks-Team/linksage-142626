"use client";

import { useState } from "react";
import Hero from "@/components/Hero";
import SummaryCard from "@/components/SummaryCard";
import TagCloud from "@/components/TagCloud";
import { fetchSummaries } from "@/lib/api";

interface Bookmark {
  id: string;
  url: string;
  title: string;
  summary: string;
}

export default function HomePage() {
  const [url, setUrl] = useState("");
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    setError("");
    try {
      const newSummary = await fetchSummaries(url);
      setBookmarks((prev) => [newSummary, ...prev]);
      setUrl("");
    } catch (err: any) {
      setError(err.message || "Failed to summarize");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="p-4">
      <Hero />
      <section className="my-8">
        <form onSubmit={handleAdd} className="flex gap-2">
          <input
            type="url"
            placeholder="Enter link to summarize"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 rounded border px-3 py-2"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            {loading ? "Summarizing…" : "Summarize"}
          </button>
        </form>
        {error && <p className="mt-2 text-red-600">{error}</p>}
      </section>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {bookmarks.map((b) => (
          <SummaryCard key={b.id} bookmark={b} />
        ))}
      </section>

      <section className="mt-8">
        <TagCloud />
      </section>
    </main>
  );
}