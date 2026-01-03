import { api } from "./axios";

export interface Project {
  projectId: string;
  projectName: string;
  description?: string;
  tags: string[];
  owner?: string;
  createdTs: string;
  modifiedTs?: string;
}

export const ProjectAPI = {
  list: () => api.get("/api/v1/project"),

  create: (payload: {
    projectName: string;
    description?: string;
    tags: string[];
    workflow: any[];
  }) => api.post("/api/v1/project", payload),

  update: (projectId: string, payload: any) =>
    api.put(`/api/v1/project/${projectId}`, payload),

  delete: (projectId: string) =>
    api.delete(`/api/v1/project/${projectId}`),
};
