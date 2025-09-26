import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface AnalyticsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  trend?: "up" | "down" | "neutral";
}

export function AnalyticsCard({ title, value, description, icon, trend }: AnalyticsCardProps) {
  const trendColors = {
    up: "text-green-600",
    down: "text-red-600", 
    neutral: "text-muted-foreground"
  };

  return (
    <Card className="hover-elevate" data-testid={`analytics-card-${title.toLowerCase().replace(/\s+/g, '-')}`}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon && <div className="h-4 w-4 text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold" data-testid="analytics-value">{value}</div>
        {description && (
          <p className={`text-xs ${trend ? trendColors[trend] : 'text-muted-foreground'}`} data-testid="analytics-description">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}