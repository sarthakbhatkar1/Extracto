import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/axios";

export default function DocumentViewer() {
  const { documentId } = useParams();
  const [doc, setDoc] = useState<any>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!documentId) return;

    const fetchDocument = async () => {
      try {
        // 1️⃣ Get metadata
        const metaRes = await api.get(`/api/v1/document/${documentId}`);
        setDoc(metaRes.data.result);

        // 2️⃣ Download file as blob (AUTHENTICATED)
        const fileRes = await api.get(
          `/api/v1/document/${documentId}/download`,
          { responseType: "blob" }
        );

        const blob = new Blob([fileRes.data], {
          type: "application/pdf",
        });

        const objectUrl = URL.createObjectURL(blob);
        setPdfUrl(objectUrl);
      } catch (err) {
        console.error("Failed to load document", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDocument();

    // Cleanup blob URL
    return () => {
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    };
  }, [documentId]);

  if (loading) {
    return <div>Loading document…</div>;
  }

  if (!doc || !pdfUrl) {
    return <div>Unable to load document</div>;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-4rem)]">
      {/* LEFT: PDF */}
      <div className="glass overflow-hidden">
        <iframe
          src={pdfUrl}
          className="w-full h-full"
          title="Document Viewer"
        />
      </div>

      {/* RIGHT: DETAILS */}
      <div className="glass p-6 space-y-6 overflow-y-auto">
        <div>
          <h2 className="text-lg font-semibold">{doc.documentName}</h2>
          <p className="text-sm text-gray-400">
            Uploaded {new Date(doc.createdTs).toLocaleString()}
          </p>
        </div>

        <div>
          <h3 className="section-title mb-2">Document Metadata</h3>
          <div className="text-sm text-gray-300 space-y-1">
            <p>Project ID: {doc.projectId}</p>
            <p>Folder: {doc.folderName}</p>
            <p>Storage: {doc.storagePath.storage_type}</p>
          </div>
        </div>

        <div>
          <h3 className="section-title mb-2">Processing Output</h3>
          <p className="text-sm text-gray-400">
            No workflows have been executed on this document yet.
          </p>
        </div>
      </div>
    </div>
  );
}
