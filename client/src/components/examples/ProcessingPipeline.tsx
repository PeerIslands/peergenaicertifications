import ProcessingPipeline from "../ProcessingPipeline";

export default function ProcessingPipelineExample() {
  return (
    <div className="p-6 max-w-xl">
      <ProcessingPipeline 
        isProcessing={true}
        onProcessingComplete={() => console.log("Processing complete!")}
      />
    </div>
  );
}
