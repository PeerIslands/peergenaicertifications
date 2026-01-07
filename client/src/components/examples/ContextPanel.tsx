import ContextPanel from "../ContextPanel";

export default function ContextPanelExample() {
  // todo: remove mock functionality
  const mockChunks = [
    {
      id: "1",
      content: "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.",
      similarity: 0.94,
      page: 3,
    },
    {
      id: "2",
      content: "Neural networks are computing systems inspired by biological neural networks that constitute animal brains. These systems learn to perform tasks by considering examples.",
      similarity: 0.82,
      page: 7,
    },
    {
      id: "3",
      content: "Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning.",
      similarity: 0.71,
      page: 12,
    },
  ];

  return (
    <div className="h-[500px] border rounded-lg overflow-hidden w-80">
      <ContextPanel 
        chunks={mockChunks}
        highlightedChunkId="1"
        onChunkClick={(id) => console.log("Chunk clicked:", id)}
      />
    </div>
  );
}
