import { UploadZone } from '../upload-zone'

export default function UploadZoneExample() {
  return (
    <UploadZone 
      onUpload={(files) => console.log('Uploaded files:', files)}
    />
  )
}