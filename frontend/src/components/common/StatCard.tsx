interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
}

const StatCard = ({ title, value, subtitle, icon }: StatCardProps) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900 mt-2">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="text-blue-600">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard;
