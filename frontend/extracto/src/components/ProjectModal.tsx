import { useState, useEffect } from "react";

interface Props {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  initialData?: any;
}

export default function ProjectModal({
  open,
  onClose,
  onSubmit,
  initialData,
}: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    if (initialData) {
      setName(initialData.projectName);
      setDescription(initialData.description || "");
    }
  }, [initialData]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="glass w-full max-w-lg p-6 space-y-4">
        <h2 className="text-xl font-semibold">
          {initialData ? "Edit Project" : "Create Project"}
        </h2>

        <input
          className="input"
          placeholder="Project Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <textarea
          className="input h-24"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-400 hover:text-white"
          >
            Cancel
          </button>

          <button
            onClick={() =>
              onSubmit({
                projectName: name,
                description,
                tags: [],
                workflow: [],
              })
            }
            className="btn-primary"
          >
            {initialData ? "Update" : "Create"}
          </button>
        </div>
      </div>
    </div>
  );
}
