import { PDFUpload } from "../PDFUpload";

export default function PDFUploadExample() {
  return (
    <div className="p-4 bg-background">
      <PDFUpload
        onUploadComplete={(files) => console.log("Upload complete:", files)}
        onClose={() => console.log("Close upload")}
      />
    </div>
  );
}
