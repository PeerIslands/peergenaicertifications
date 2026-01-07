import UploadZone from "../UploadZone";

export default function UploadZoneExample() {
  return (
    <div className="p-6 max-w-md">
      <UploadZone 
        onFileUpload={(file) => console.log("File uploaded:", file)} 
        uploadedFile={{
          name: "sample-document.pdf",
          size: 2456789,
          pages: 15,
        }}
      />
    </div>
  );
}
