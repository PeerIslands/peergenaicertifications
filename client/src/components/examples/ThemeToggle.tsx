import { ThemeToggle } from '../ThemeToggle';

export default function ThemeToggleExample() {
  return (
    <div className="p-4">
      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">Theme:</span>
        <ThemeToggle />
      </div>
    </div>
  );
}