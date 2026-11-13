"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const EXAMPLES = [
  "How many depts are there?",
  "What is department 007?",
  "List all Engineering departments",
  "How many departments are in APAC?",
  "Which departments deal with security or compliance?",
];

type Result = {
  query: string;
  sql: string;
  columns: string[];
  rows: (string | number | null)[][];
  answer: string;
  model: string;
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function ask(q: string) {
    const question = q.trim();
    if (!question || loading) return;
    setQuery(question);
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail ?? `Request failed (${res.status})`);
      setResult(data);
    } catch (e) {
      setError(
        e instanceof TypeError
          ? `Can't reach the API at ${API_URL}. Start the backend and try again.`
          : (e as Error).message,
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-3xl px-4 py-12 sm:py-20">
      <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
        Ask the department directory
      </h1>
      <p className="mt-3 max-w-xl text-muted">
        Type a question in plain English. The AI writes the SQL, runs it against 100
        departments, and explains what it found.
      </p>

      <form
        className="mt-8 rounded-lg border border-line bg-panel p-2 shadow-[0_1px_0_#d3dae2] focus-within:border-gemini"
        onSubmit={(e) => {
          e.preventDefault();
          ask(query);
        }}
      >
        <label htmlFor="q" className="sr-only">
          Your question
        </label>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            id="q"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="How many depts are there?"
            className="min-w-0 flex-1 rounded-md bg-transparent px-3 py-3 text-lg outline-none placeholder:text-muted/60"
            autoFocus
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="rounded-md bg-ink px-5 py-3 font-medium text-white transition-colors hover:bg-gemini focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gemini disabled:opacity-40 disabled:hover:bg-ink"
          >
            {loading ? "Asking…" : "Ask"}
          </button>
        </div>
      </form>

      <div className="mt-4 flex flex-wrap gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => ask(ex)}
            disabled={loading}
            className="rounded-full border border-line px-3 py-1 text-sm text-muted hover:border-ink hover:text-ink focus-visible:outline-2 focus-visible:outline-gemini disabled:opacity-40"
          >
            {ex}
          </button>
        ))}
      </div>

      <section aria-live="polite" className="mt-12">
        {loading && <Pending />}
        {error && (
          <div className="reveal rounded-lg border border-answer/40 bg-answer/5 p-4 text-sm">
            <p className="font-medium text-answer">That question didn&apos;t go through.</p>
            <p className="mt-1 break-words text-ink">{error}</p>
          </div>
        )}
        {result && <Trace result={result} />}
      </section>
    </main>
  );
}

function Pending() {
  return (
    <div className="flex items-center gap-3 text-muted">
      <span className="size-2 animate-pulse rounded-full bg-gemini" />
      Writing SQL and reading the table…
    </div>
  );
}

function Step({
  n,
  title,
  color,
  last,
  children,
}: {
  n: number;
  title: string;
  color: string;
  last?: boolean;
  children: React.ReactNode;
}) {
  return (
    <li className="relative grid grid-cols-[2rem_1fr] gap-4">
      <div className="flex flex-col items-center">
        <span
          className="grid size-7 place-items-center rounded-full text-xs font-semibold text-white"
          style={{ background: color }}
        >
          {n}
        </span>
        {!last && <span className="mt-1 w-px flex-1 bg-line" />}
      </div>
      <div className="min-w-0 pb-8">
        <h2 className="text-sm font-medium text-muted">{title}</h2>
        <div className="mt-2">{children}</div>
      </div>
    </li>
  );
}

function Trace({ result }: { result: Result }) {
  return (
    <div className="reveal">
      <p className="whitespace-pre-line border-l-4 border-answer pl-5 text-2xl leading-snug sm:text-[1.75rem]">
        {result.answer}
      </p>

      <h2 className="mt-14 mb-6 text-lg font-semibold">How this answer was found</h2>
      <ol>
        <Step n={1} title="Your question" color="var(--color-ink)">
          <p>{result.query}</p>
        </Step>
        <Step n={2} title={`SQL written by ${result.model}`} color="var(--color-gemini)">
          <pre className="overflow-x-auto rounded-md bg-ink p-4 font-mono text-sm leading-relaxed text-[#c9f2e9]">
            {result.sql}
          </pre>
        </Step>
        <Step
          n={3}
          title={`Rows returned from the dept table (${result.rows.length})`}
          color="var(--color-muted)"
        >
          <Rows columns={result.columns} rows={result.rows} />
        </Step>
        <Step n={4} title="Friendly answer" color="var(--color-answer)" last>
          <p className="text-muted">The model turned the question and rows into the answer above.</p>
        </Step>
      </ol>
    </div>
  );
}

function Rows({ columns, rows }: { columns: string[]; rows: Result["rows"] }) {
  if (rows.length === 0) return <p className="text-muted">No rows matched.</p>;
  return (
    <div className="max-h-80 overflow-auto rounded-md border border-line bg-panel">
      <table className="w-full text-left text-sm">
        <thead className="sticky top-0 bg-paper">
          <tr>
            {columns.map((c) => (
              <th key={c} className="px-3 py-2 font-medium">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t border-line align-top">
              {r.map((v, j) => (
                <td key={j} className="px-3 py-2 tabular-nums">
                  {v === null ? <span className="text-muted">null</span> : String(v)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
