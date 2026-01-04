import { api } from "./axios";

export interface Task {
  taskId: string;
  documentIds: string[];
  status: string;
  output: Record<string, any>;
  createdTs: string;
  modifiedTs: string;
}

export const TaskAPI = {
  listByUser: () =>
    api.get("/api/v1/task"),

  create: (documentIds: string[]) =>
    api.post("/api/v1/task", {
      documentIds,
    }),

  getById: (taskId: string) =>
    api.get(`/api/v1/task/${taskId}`),
};
