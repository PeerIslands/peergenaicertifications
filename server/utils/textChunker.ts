function getPositiveInt(value: string | undefined, fallback: number): number {
  if (!value?.trim()) {
    return fallback;
  }

  const parsed = Number.parseInt(value, 10);
  if (Number.isNaN(parsed) || parsed <= 0) {
    return fallback;
  }

  return parsed;
}

const DEFAULT_CHUNK_SIZE = getPositiveInt(process.env.CHUNK_SIZE, 1200);
const DEFAULT_CHUNK_OVERLAP_RAW = getPositiveInt(
  process.env.CHUNK_OVERLAP,
  200
);
const DEFAULT_CHUNK_OVERLAP = Math.min(
  DEFAULT_CHUNK_OVERLAP_RAW,
  Math.floor(DEFAULT_CHUNK_SIZE / 2)
);

/**
 * Split long document text into overlapping chunks to keep embeddings focused.
 */
export function chunkText(
  text: string,
  chunkSize: number = DEFAULT_CHUNK_SIZE,
  chunkOverlap: number = DEFAULT_CHUNK_OVERLAP
): string[] {
  const normalized = text.replace(/\r\n/g, "\n").trim();
  if (!normalized) {
    return [];
  }

  const effectiveOverlap = Math.min(chunkOverlap, Math.floor(chunkSize / 2));
  const chunks: string[] = [];
  let start = 0;

  while (start < normalized.length) {
    const baseEnd = Math.min(start + chunkSize, normalized.length);
    let end = baseEnd;
    let chunk = normalized.slice(start, end);

    if (end < normalized.length) {
      const window = chunk;
      const breakPoints = [
        window.lastIndexOf("\n\n"),
        window.lastIndexOf("\n"),
        window.lastIndexOf(". "),
        window.lastIndexOf("? "),
        window.lastIndexOf("! "),
        window.lastIndexOf(" "),
      ];

      const preferredBreak = breakPoints
        .filter(
          (index) => index !== -1 && index > Math.floor(window.length * 0.6)
        )
        .sort((a, b) => b - a)[0];

      if (preferredBreak !== undefined) {
        end = start + preferredBreak + 1;
        chunk = normalized.slice(start, end);
      }
    }

    const trimmedChunk = chunk.trim();
    if (trimmedChunk.length > 0) {
      chunks.push(trimmedChunk);
    }

    if (end >= normalized.length) {
      break;
    }

    start = end - effectiveOverlap;
    if (start < 0) {
      start = 0;
    }
    if (start >= normalized.length) {
      break;
    }
  }

  return chunks;
}
