import { UploadZone } from '../upload-zone'
import { clientLogger } from "@/lib/logger";

export default function UploadZoneExample() {
  return (
    <UploadZone 
      onUpload={(files) => clientLogger.info('Uploaded files', { count: files.length })}
    />
  )
}