import { FileUploadZone } from '../FileUploadZone';

export default function FileUploadZoneExample() {
  const handleFileSelect = (file: File) => {
    //console.log('File selected:', file.name);
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <FileUploadZone 
        onFileSelect={handleFileSelect}
        isUploading={false}
      />
    </div>
  );
}