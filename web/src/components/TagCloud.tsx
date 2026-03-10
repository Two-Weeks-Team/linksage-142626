"use client";

import { useEffect, useState } from "react";
import { fetchTags } from "@/lib/api";

export function TagCloud() {
  const [tags, setTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const recent = await fetchTags(""); // backend can return recent/global tags when URL empty
        setTags(recent);
      } catch {
        setTags([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <p>Loading tags…</p>;

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => (
        <span
          key={tag}
          className="rounded bg-gray-200 px-2 py-1 text-sm"
        >
          {tag}
        </span>
      ))}
    </div>
  );
}

export default TagCloud
