import DocumentSidebar from "../DocumentSidebar";

export default function DocumentSidebarExample() {
  // todo: remove mock functionality
  const mockDocuments = [
    {
      id: "1",
      name: "machine-learning-basics.pdf",
      pages: 15,
      chunks: 24,
      uploadedAt: new Date(),
    },
    {
      id: "2",
      name: "neural-networks-guide.pdf",
      pages: 32,
      chunks: 48,
      uploadedAt: new Date(Date.now() - 86400000),
    },
  ];

  return (
    <div className="h-[500px] w-64 border rounded-lg overflow-hidden">
      <DocumentSidebar
        documents={mockDocuments}
        selectedDocumentId="1"
        chunkSettings={{ chunkSize: 500, overlap: 50 }}
        onSelectDocument={(id) => console.log("Selected:", id)}
        onRemoveDocument={(id) => console.log("Remove:", id)}
        onSettingsChange={(settings) => console.log("Settings:", settings)}
      />
    </div>
  );
}
