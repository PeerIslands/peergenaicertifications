import { AnalyticsCard } from '../AnalyticsCard';
import { MessageSquare, Clock, TrendingUp, Zap } from 'lucide-react';

export default function AnalyticsCardExample() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <AnalyticsCard 
        title="Total Messages"
        value="247"
        description="+12% from last hour"
        icon={<MessageSquare />}
        trend="up"
      />
      <AnalyticsCard 
        title="Avg Response Time"
        value="1.2s"
        description="+0.1s from baseline"
        icon={<Clock />}
        trend="down"
      />
      <AnalyticsCard 
        title="Conversations"
        value="18"
        description="Active sessions"
        icon={<TrendingUp />}
        trend="neutral"
      />
      <AnalyticsCard 
        title="Response Rate"
        value="98.5%"
        description="System uptime"
        icon={<Zap />}
        trend="up"
      />
    </div>
  );
}