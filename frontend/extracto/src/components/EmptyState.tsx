export interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="glass p-12 text-center max-w-xl mx-auto space-y-4">
      <h3 className="text-2xl font-semibold">{title}</h3>

      <p className="text-slate-400 text-sm leading-relaxed">{description}</p>

      {actionLabel && onAction && (
        <button onClick={onAction} className="btn-primary mt-4">
          {actionLabel}
        </button>
      )}
    </div>
  );
}
