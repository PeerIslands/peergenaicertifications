import EmptyState from "../EmptyState";

export default function EmptyStateExample() {
  const handlePromptClick = (prompt: string) => {
    console.log("Prompt clicked:", prompt);
  };

  return (
    <div className="h-screen bg-background">
      <EmptyState onPromptClick={handlePromptClick} />
    </div>
  );
}
