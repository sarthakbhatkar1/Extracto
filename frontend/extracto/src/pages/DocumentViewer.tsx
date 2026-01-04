import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/axios";
import { TaskAPI } from "../api/task.api";
import type { Task } from "../api/task.api";

export default function DocumentViewer() {
  const { documentId } = useParams();
  const [doc, setDoc] = useState<any>(null);
  const [task, setTask] = useState<Task | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!documentId) return;

    const load = async () => {
      // Document metadata
      const docRes = await api.get(`/api/v1/document/${documentId}`);
      setDoc(docRes.data.result);

      // Download file
      const fileRes = await api.get(`/api/v1/document/${documentId}/download`, {
        responseType: "blob",
      });

      const blob = new Blob([fileRes.data], {
        type: "application/pdf",
      });
      setPdfUrl(URL.createObjectURL(blob));

      // Load task
      const taskRes = await TaskAPI.listByUser();
      const related = taskRes.data.result.find((t: Task) =>
        t.documentIds.includes(documentId)
      );
      setTask(related || null);
    };

    load();

    return () => {
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    };
  }, [documentId]);

  if (!doc || !pdfUrl) {
    return <div>Loading document…</div>;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-4rem)]">
      {/* PDF */}
      <div className="glass overflow-hidden">
        <iframe src={pdfUrl} className="w-full h-full" title="Document" />
      </div>

      {/* Task + Details */}
      <div className="glass p-6 space-y-6 overflow-y-auto">
        <div>
          <h2 className="text-lg font-semibold">{doc.documentName}</h2>
          <p className="text-sm text-slate-400">
            Uploaded {new Date(doc.createdTs).toLocaleString()}
          </p>
        </div>

        <div>
          <h3 className="section-title">Task Status</h3>

          {task ? (
            <>
              <p className="text-sm mt-2">
                Status: <span className="font-medium">{task.status}</span>
              </p>

              <p className="text-xs text-slate-400 mt-1">
                Created {new Date(task.createdTs).toLocaleString()}
              </p>

              <div className="mt-4">
                <h4 className="text-sm font-medium">Output</h4>
                <pre className="mt-2 text-xs bg-black/40 p-3 rounded overflow-auto">
                  {JSON.stringify(task.output, null, 2)}
                </pre>
              </div>
            </>
          ) : (
            <p className="text-sm text-slate-400">
              No task created for this document.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
