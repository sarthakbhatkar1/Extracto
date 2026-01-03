import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { DocumentAPI } from "../api/document.api";
import UploadDocumentModal from "../components/UploadDocumentModal";

export default function ProjectDocuments() {
  const { projectId } = useParams();
  const [project, setProject] = useState<any>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  const fetchDocs = async () => {
    if (!projectId) return;
    const res = await DocumentAPI.getByProject(projectId);
    setProject(res.data.result);
  };

  useEffect(() => {
    fetchDocs();
  }, [projectId]);

  if (!project) return null;

  const folders = [...project.folders].sort((a: any, b: any) =>
    a.folderName.localeCompare(b.folderName)
  );

  const folderNames = folders.map((f: any) => f.folderName);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">{project.projectName}</h1>
          <p className="text-gray-400 text-sm">
            Documents organized by folders
          </p>
        </div>

        <button onClick={() => setShowUpload(true)} className="btn-primary">
          Upload Document
        </button>
      </div>

      {/* Folders */}
      <div className="space-y-4">
        {folders.map((folder: any) => (
          <div key={folder.folderName} className="glass">
            <button
              className="w-full flex justify-between items-center p-4"
              onClick={() =>
                setExpanded(
                  expanded === folder.folderName ? null : folder.folderName
                )
              }
            >
              <span className="font-medium">{folder.folderName}</span>
              <span className="text-sm text-gray-400">
                {folder.documents.length} documents
              </span>
            </button>

            {expanded === folder.folderName && (
              <div className="border-t border-white/10">
                {folder.documents.map((doc: any) => (
                  <Link
                    key={doc.documentId}
                    to={`/documents/${doc.documentId}`}
                    className="block px-6 py-3 hover:bg-white/5 text-sm"
                  >
                    {doc.documentName}
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Upload Modal */}
      <UploadDocumentModal
        open={showUpload}
        projectId={projectId!}
        existingFolders={folderNames}
        onClose={() => setShowUpload(false)}
        onSuccess={fetchDocs}
      />
    </div>
  );
}
