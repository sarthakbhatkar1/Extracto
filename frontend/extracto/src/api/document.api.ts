import { api } from "./axios";

export const DocumentAPI = {
  getByProject: (projectId: string) =>
    api.get(`/api/v1/project/${projectId}/documents`),

  upload: (formData: FormData) =>
    api.post("/api/v1/document", formData),

  get: (documentId: string) =>
    api.get(`/api/v1/document/${documentId}`),

  downloadUrl: (documentId: string) =>
    `http://localhost:7777/api/v1/document/${documentId}/download`,
};
