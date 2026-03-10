"use client";

interface Bookmark {
  id: string;
  url: string;
  title: string;
  summary: string;
}

export function SummaryCard({ bookmark }: { bookmark: Bookmark }) {
  const [showFull, setShowFull] = useState(false);
  return (
    <div className="rounded border p-4 shadow hover:shadow-lg">
      <h3 className="font-semibold text-lg">
        {bookmark.title || bookmark.url}
      </h3>
      <p className="mt-2 text-gray-700">
        {showFull ? bookmark.summary : `${bookmark.summary.slice(0, 120)}...`}
      </p>
      <a
        href={bookmark.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-2 block text-blue-600 hover:underline"
      >
        Visit site
      </a>
      <button
        onClick={() => setShowFull((v) => !v)}
        className="mt-2 text-sm text-gray-500 underline"
      >
        {showFull ? "Show less" : "Show more"}
      </button>
    </div>
  );
}

import { useState } from "react";

export default SummaryCard
