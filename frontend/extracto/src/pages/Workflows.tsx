import { useState } from "react";
import EmptyState from "../components/EmptyState";

interface Workflow {
  workflowId: string;
  name: string;
  type: string;
  description: string;
  createdAt: string;
}

export default function Workflows() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);

  if (workflows.length === 0) {
    return (
      <EmptyState
        title="No workflows created"
        description="Workflows define how documents are processed and analyzed. Create reusable workflows and attach them to projects."
        actionLabel="Create workflow"
        onAction={() => alert("Workflow creation coming next")}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Workflows</h1>
          <p className="text-gray-400 text-sm">
            Define reusable document processing pipelines.
          </p>
        </div>

        <button className="btn-primary">+ New Workflow</button>
      </div>

      <div className="glass overflow-hidden">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Description</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {workflows.map((wf) => (
              <tr key={wf.workflowId} className="table-row">
                <td className="font-medium">{wf.name}</td>
                <td className="text-gray-400">{wf.type}</td>
                <td className="text-gray-400">{wf.description}</td>
                <td className="text-gray-400">
                  {new Date(wf.createdAt).toLocaleDateString()}
                </td>
                <td className="flex gap-2 justify-end">
                  <button className="text-xs text-blue-400">Edit</button>
                  <button className="text-xs text-red-400">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
