// Formats a count like social apps do: 1,204 / 12.4K / 412K / 1.2M.
export const formatCount = (n: number) => {
  const v = Math.round(n);
  if (v < 10_000) return v.toLocaleString("en-US");
  if (v < 100_000) return `${(v / 1000).toFixed(1).replace(/\.0$/, "")}K`;
  if (v < 1_000_000) return `${Math.round(v / 1000)}K`;
  return `${(v / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
};
