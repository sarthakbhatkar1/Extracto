import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import toast from "react-hot-toast";

import { api } from "../api/axios";
import { TaskAPI } from "../api/task.api";
import UploadDocumentModal from "../components/UploadDocumentModal";

interface DocumentItem {
  documentId: string;
  documentName: string;
  createdTs: string;
}

interface Folder {
  folderName: string;
  documents: DocumentItem[];
}

interface Task {
  taskId: string;
  documentIds: string[];
  status: string;
}

export default function ProjectDocuments() {
  const { projectId } = useParams<{ projectId: string }>();

  const [folders, setFolders] = useState<Folder[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  // Upload modal state
  const [showUpload, setShowUpload] = useState(false);
  const [uploadFolder, setUploadFolder] = useState<string | null>(null);

  const loadData = async () => {
    if (!projectId) return;

    try {
      setLoading(true);

      const [docsRes, taskRes] = await Promise.all([
        api.get(`/api/v1/document?projectId=${projectId}`),
        TaskAPI.listByUser(),
      ]);

      const projectData = docsRes.data.result?.[0];
      setFolders(projectData?.folders || []);
      setTasks(taskRes.data.result || []);
    } catch (err) {
      console.error(err);
      toast.error("Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  const getTaskStatus = (documentId: string) => {
    const task = tasks.find((t) => t.documentIds.includes(documentId));
    return task?.status || "Not Started";
  };

  if (loading) {
    return <div className="text-sm text-slate-400">Loading…</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Document Management</h1>
          <p className="text-sm text-slate-400">
            Documents organized by folder with processing status.
          </p>
        </div>

        {/* GLOBAL UPLOAD */}
        <button
          className="btn-primary"
          onClick={() => {
            setUploadFolder(null);
            setShowUpload(true);
          }}
        >
          Upload Document
        </button>
      </div>

      {/* Empty State */}
      {folders.length === 0 && (
        <div className="glass p-10 text-center max-w-xl">
          <h2 className="text-lg font-semibold mb-2">No documents yet</h2>
          <p className="text-sm text-slate-400 mb-6">
            Upload your first document to start processing.
          </p>
        </div>
      )}

      {/* Folders */}
      {folders.map((folder) => (
        <div key={folder.folderName} className="glass p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="font-semibold">
              {folder.folderName} ({folder.documents.length})
            </h2>

            {/* FOLDER UPLOAD */}
            <button
              className="btn-secondary"
              onClick={() => {
                setUploadFolder(folder.folderName);
                setShowUpload(true);
              }}
            >
              Upload
            </button>
          </div>

          <table className="w-full text-sm">
            <thead className="text-slate-400 border-b border-white/10">
              <tr>
                <th className="text-left py-2">Document</th>
                <th className="text-left py-2">Status</th>
                <th className="text-left py-2">Created</th>
              </tr>
            </thead>
            <tbody>
              {folder.documents.map((doc) => (
                <tr key={doc.documentId} className="border-b border-white/5">
                  <td className="py-2 text-blue-400">{doc.documentName}</td>
                  <td className="py-2">
                    <span className="px-2 py-1 rounded bg-yellow-400/20 text-yellow-400 text-xs">
                      {getTaskStatus(doc.documentId)}
                    </span>
                  </td>
                  <td className="py-2 text-slate-400">
                    {new Date(doc.createdTs).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      {/* Upload Modal */}
      <UploadDocumentModal
        open={showUpload}
        projectId={projectId!}
        existingFolders={folders.map((f) => f.folderName)}
        defaultFolder={uploadFolder}
        onClose={() => setShowUpload(false)}
        onSuccess={loadData}
      />
    </div>
  );
}
