import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
// import { ProjectAPI, Project } from "../api/project.api";
import { ProjectAPI } from "../api/project.api";
import type { Project } from "../api/project.api";
import ProjectModal from "../components/ProjectModal";
import DeleteConfirm from "../components/DeleteConfirm";
import EmptyState from "../components/EmptyState";

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const [showModal, setShowModal] = useState(false);
  const [editProject, setEditProject] = useState<Project | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null);

  const fetchProjects = async () => {
    setLoading(true);
    const res = await ProjectAPI.list();
    setProjects(res.data.result);
    setLoading(false);
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateOrUpdate = async (data: any) => {
    try {
      if (editProject) {
        await ProjectAPI.update(editProject.projectId, data);
        toast.success("Project updated");
      } else {
        await ProjectAPI.create(data);
        toast.success("Project created");
      }
      setShowModal(false);
      setEditProject(null);
      fetchProjects();
    } catch {
      toast.error("Operation failed");
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await ProjectAPI.delete(deleteTarget.projectId);
      toast.success("Project deleted");
      setDeleteTarget(null);
      fetchProjects();
    } catch {
      toast.error("Delete failed");
    }
  };

  if (!loading && projects.length === 0) {
    return (
      <>
        <EmptyState
          title="No projects yet"
          description="Projects help you organize documents by use-case, client, or workflow. Each project can contain folders and documents."
          actionLabel="Create your first project"
          onAction={() => setShowModal(true)}
        />

        <ProjectModal
          open={showModal}
          onClose={() => setShowModal(false)}
          onSubmit={handleCreateOrUpdate}
        />
      </>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold">Projects</h1>
          <p className="text-gray-400 text-sm">
            Organize documents and workflows by project.
          </p>
        </div>

        <button onClick={() => setShowModal(true)} className="btn-primary">
          + New Project
        </button>
      </div>

      <div className="glass overflow-hidden">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Tags</th>
              <th>Description</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {projects.map((p) => (
              <tr key={p.projectId} className="table-row">
                <td>
                  <Link
                    to={`/projects/${p.projectId}`}
                    className="text-blue-400 hover:underline font-medium"
                  >
                    {p.projectName}
                  </Link>
                </td>

                <td className="text-slate-400">
                  {p.tags?.length ? p.tags.join(", ") : "—"}
                </td>

                <td className="text-slate-400">{p.description || "—"}</td>

                <td className="text-slate-400">
                  {new Date(p.createdTs).toLocaleDateString()}
                </td>

                <td className="flex gap-2 justify-end">
                  <button className="text-xs text-blue-400 hover:underline">
                    Edit
                  </button>
                  <button className="text-xs text-red-400 hover:underline">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ProjectModal
        open={showModal}
        onClose={() => {
          setShowModal(false);
          setEditProject(null);
        }}
        onSubmit={handleCreateOrUpdate}
        initialData={editProject}
      />

      <DeleteConfirm
        open={!!deleteTarget}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
      />
    </div>
  );
}
