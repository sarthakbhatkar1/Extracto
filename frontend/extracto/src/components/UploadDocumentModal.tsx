import { useState } from "react";
import toast from "react-hot-toast";
import { DocumentAPI } from "../api/document.api";

interface Props {
  open: boolean;
  projectId: string;
  existingFolders: string[];
  onClose: () => void;
  onSuccess: () => void;
}

export default function UploadDocumentModal({
  open,
  projectId,
  existingFolders,
  onClose,
  onSuccess,
}: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [folder, setFolder] = useState("");
  const [newFolder, setNewFolder] = useState("");
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a file");
      return;
    }

    const folderName = newFolder || folder;
    if (!folderName) {
      toast.error("Please select or enter a folder");
      return;
    }

    const formData = new FormData();
    formData.append("projectId", projectId);
    formData.append("folderName", folderName);
    formData.append("documentType", "PDF");
    formData.append("document", file);

    try {
      setLoading(true);
      await DocumentAPI.upload(formData);
      toast.success("Document uploaded successfully");
      onSuccess();
      onClose();
    } catch {
      toast.error("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center">
      <div className="glass w-full max-w-lg p-6 space-y-5">
        <h2 className="text-xl font-semibold">Upload Document</h2>

        {/* File */}
        <div>
          <label className="text-sm text-gray-400">Document (PDF)</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="input mt-2"
          />
        </div>

        {/* Folder selection */}
        <div>
          <label className="text-sm text-gray-400">Folder</label>

          <select
            className="input mt-2"
            value={folder}
            onChange={(e) => setFolder(e.target.value)}
          >
            <option value="">Select existing folder</option>
            {existingFolders.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>

          <input
            className="input mt-2"
            placeholder="Or create new folder"
            value={newFolder}
            onChange={(e) => setNewFolder(e.target.value)}
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4">
          <button onClick={onClose} className="text-sm text-gray-400">
            Cancel
          </button>

          <button
            onClick={handleUpload}
            disabled={loading}
            className="btn-primary disabled:opacity-50"
          >
            {loading ? "Uploading..." : "Upload"}
          </button>
        </div>
      </div>
    </div>
  );
}
