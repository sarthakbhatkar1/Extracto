import { Link } from "react-router-dom";

export default function Dashboard() {
  /**
   * These will come from APIs later.
   * Hardcoded for now but STRUCTURALLY CORRECT.
   */
  const stats = {
    projects: 3,
    documents: 18,
    workflows: 2,
    processedToday: 6,
  };

  const recentDocuments = [
    {
      id: "1",
      name: "Invoice_Jan.pdf",
      project: "Finance Ops",
      status: "Processed",
    },
    {
      id: "2",
      name: "LPA_Agreement.pdf",
      project: "Legal",
      status: "Pending",
    },
    {
      id: "3",
      name: "KYC_Form.pdf",
      project: "Onboarding",
      status: "Processed",
    },
  ];

  return (
    <div className="space-y-10">
      {/* ================= HEADER ================= */}
      <div>
        <h1 className="text-3xl font-semibold">System Overview</h1>
        <p className="text-slate-400 mt-1">
          Monitor document activity, processing status, and workflows across
          your workspace.
        </p>
      </div>

      {/* ================= KPI ROW ================= */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          label="Active Projects"
          value={stats.projects}
          description="Logical containers for documents"
        />
        <StatCard
          label="Documents Ingested"
          value={stats.documents}
          description="Total uploaded documents"
        />
        <StatCard
          label="Workflows Defined"
          value={stats.workflows}
          description="Reusable processing logic"
        />
        <StatCard
          label="Processed Today"
          value={stats.processedToday}
          description="Documents analyzed today"
        />
      </div>

      {/* ================= MAIN GRID ================= */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ---------- LEFT (2 cols) ---------- */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Documents */}
          <div className="glass p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="section-title">Recent Documents</h2>
              <Link
                to="/projects"
                className="text-sm text-blue-400 hover:underline"
              >
                View all
              </Link>
            </div>

            <table className="table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Project</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentDocuments.map((doc) => (
                  <tr key={doc.id} className="table-row">
                    <td className="font-medium">{doc.name}</td>
                    <td className="text-slate-400">{doc.project}</td>
                    <td>
                      <span
                        className={
                          doc.status === "Processed"
                            ? "badge badge-green"
                            : "badge badge-yellow"
                        }
                      >
                        {doc.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Project Health */}
          <div className="glass p-6">
            <h2 className="section-title mb-3">Project Health</h2>
            <p className="text-sm text-slate-400 mb-4">
              High-level view of document distribution across projects.
            </p>

            <div className="space-y-3">
              <HealthRow name="Finance Ops" count={8} />
              <HealthRow name="Legal" count={6} />
              <HealthRow name="Onboarding" count={4} />
            </div>
          </div>
        </div>

        {/* ---------- RIGHT (1 col) ---------- */}
        <div className="space-y-6">
          {/* Guided Actions */}
          <div className="glass p-6">
            <h2 className="section-title mb-3">Recommended Actions</h2>

            <ul className="space-y-3 text-sm text-slate-300">
              <li>• Create a new workflow for invoice processing</li>
              <li>• Upload pending documents to the Legal project</li>
              <li>• Review documents awaiting workflow execution</li>
            </ul>

            <Link to="/projects" className="btn-primary w-full mt-5">
              Go to Projects
            </Link>
          </div>

          {/* System Explanation */}
          <div className="glass p-6">
            <h2 className="section-title mb-3">How Extracto Works</h2>

            <ol className="list-decimal list-inside text-sm text-slate-300 space-y-2">
              <li>Projects represent business or operational use-cases.</li>
              <li>Documents are uploaded and organized into folders.</li>
              <li>Workflows define how content is extracted or analyzed.</li>
              <li>Results are reviewed at the document level.</li>
            </ol>

            <p className="text-xs text-slate-400 mt-4">
              Extracto is designed for repeatable, auditable document
              intelligence at scale.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ================= SUB COMPONENTS ================= */

function StatCard({
  label,
  value,
  description,
}: {
  label: string;
  value: number;
  description: string;
}) {
  return (
    <div className="glass p-6">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="text-3xl font-semibold mt-2">{value}</p>
      <p className="text-xs text-slate-500 mt-1">{description}</p>
    </div>
  );
}

function HealthRow({ name, count }: { name: string; count: number }) {
  return (
    <div className="flex justify-between items-center text-sm">
      <span>{name}</span>
      <span className="text-slate-400">{count} documents</span>
    </div>
  );
}
