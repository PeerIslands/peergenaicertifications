import { AnalyticsDashboard } from '../AnalyticsDashboard';

export default function AnalyticsDashboardExample() {
  const mockAnalytics = {
    totalMessages: 247,
    averageResponseTime: 1247, // milliseconds
    conversationCount: 18,
    systemUptime: 98.5,
  };

  return (
    <div className="max-w-full">
      <AnalyticsDashboard {...mockAnalytics} />
    </div>
  );
}