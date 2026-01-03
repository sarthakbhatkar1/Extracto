import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../api/axios";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const [project, setProject] = useState<any>(null);

  useEffect(() => {
    api.get(`/api/v1/project/${projectId}`).then((res) => setProject(res.data));
  }, [projectId]);

  if (!project) return null;

  return (
    <div>
      <h1 className="text-2xl font-semibold">{project.projectName}</h1>

      {project.folders.map((folder: any) => (
        <div key={folder.folderName} className="glass p-4 mt-6">
          <h3 className="font-medium">
            {folder.folderName} ({folder.documents.length})
          </h3>

          <ul className="mt-2 space-y-2">
            {folder.documents.map((doc: any) => (
              <li key={doc.documentId} className="flex justify-between">
                <span>{doc.documentName}</span>
                <a
                  className="text-blue-400"
                  href={`http://localhost:7777/api/v1/document/${doc.documentId}/download`}
                >
                  Download
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
