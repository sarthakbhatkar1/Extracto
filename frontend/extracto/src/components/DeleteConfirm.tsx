interface Props {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function DeleteConfirm({ open, onConfirm, onCancel }: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="glass p-6 w-full max-w-sm">
        <h3 className="text-lg font-medium">Delete Project</h3>
        <p className="text-sm text-gray-400 mt-2">
          This action cannot be undone.
        </p>

        <div className="flex justify-end gap-3 mt-6">
          <button onClick={onCancel} className="text-sm text-gray-400">
            Cancel
          </button>

          <button
            onClick={onConfirm}
            className="bg-red-600 px-4 py-2 rounded text-sm"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
