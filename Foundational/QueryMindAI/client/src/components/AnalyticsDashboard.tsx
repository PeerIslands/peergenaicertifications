import { AnalyticsCard } from "./AnalyticsCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { MessageSquare, Clock, TrendingUp, Zap } from "lucide-react";

interface AnalyticsDashboardProps {
  totalMessages: number;
  averageResponseTime: number;
  conversationCount: number;
  systemUptime: number;
}

/**
 * Dashboard component that displays comprehensive analytics including metrics cards, charts, and recent activity.
 * 
 * @param props - Component props
 * @param props.totalMessages - Total number of messages in the session
 * @param props.averageResponseTime - Average response time in milliseconds
 * @param props.conversationCount - Number of conversations in the session
 * @param props.systemUptime - System uptime percentage
 * @returns A React component rendering an analytics dashboard with charts and metrics
 */
export function AnalyticsDashboard({ 
  totalMessages, 
  averageResponseTime, 
  conversationCount,
  systemUptime 
}: AnalyticsDashboardProps) {
  // Mock data for charts - todo: remove mock functionality
  const responseTimeData = [
    { time: '10:00', responseTime: 1200 },
    { time: '10:15', responseTime: 980 },
    { time: '10:30', responseTime: 1100 },
    { time: '10:45', responseTime: 890 },
    { time: '11:00', responseTime: 1340 },
    { time: '11:15', responseTime: 1150 },
  ];

  const messageVolumeData = [
    { hour: '9AM', messages: 12 },
    { hour: '10AM', messages: 25 },
    { hour: '11AM', messages: 18 },
    { hour: '12PM', messages: 32 },
    { hour: '1PM', messages: 28 },
    { hour: '2PM', messages: 22 },
  ];

  return (
    <div className="space-y-6 p-6" data-testid="analytics-dashboard">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <AnalyticsCard
          title="Total Messages"
          value={totalMessages}
          description={totalMessages > 0 ? "+12% from last hour" : "No messages yet"}
          icon={<MessageSquare />}
          trend={totalMessages > 50 ? "up" : "neutral"}
        />
        <AnalyticsCard
          title="Avg Response Time"
          value={`${(averageResponseTime / 1000).toFixed(1)}s`}
          description={averageResponseTime < 2000 ? "Excellent performance" : "Above baseline"}
          icon={<Clock />}
          trend={averageResponseTime < 1500 ? "up" : "down"}
        />
        <AnalyticsCard
          title="Conversations"
          value={conversationCount}
          description="Active sessions"
          icon={<TrendingUp />}
          trend="neutral"
        />
        <AnalyticsCard
          title="System Status"
          value={`${systemUptime.toFixed(1)}%`}
          description="Uptime"
          icon={<Zap />}
          trend="up"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Response Time Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={responseTimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="responseTime" 
                  stroke="hsl(var(--chart-1))" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Message Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={messageVolumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="messages" fill="hsl(var(--chart-2))" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3" data-testid="recent-activity">
            {/* Mock recent activity - todo: remove mock functionality */}
            <div className="flex items-center justify-between text-sm">
              <span>User asked about machine learning</span>
              <span className="text-muted-foreground">2 min ago</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>AI response completed in 1.2s</span>
              <span className="text-muted-foreground">2 min ago</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span>New conversation started</span>
              <span className="text-muted-foreground">5 min ago</span>
            </div>
            {totalMessages === 0 && (
              <div className="text-center text-muted-foreground py-4">
                No activity yet. Start a conversation to see analytics!
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}