import { Link } from "react-router-dom";

interface Crumb {
  label: string;
  path?: string;
}

export default function Breadcrumb({ items }: { items: Crumb[] }) {
  return (
    <nav className="text-sm text-gray-400 mb-4">
      {items.map((item, index) => (
        <span key={index}>
          {item.path ? (
            <Link to={item.path} className="hover:text-white">
              {item.label}
            </Link>
          ) : (
            <span className="text-white">{item.label}</span>
          )}
          {index < items.length - 1 && " / "}
        </span>
      ))}
    </nav>
  );
}
