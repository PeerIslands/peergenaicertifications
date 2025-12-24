import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/lib/theme";
import Chat from "@/pages/Chat";
import NotFound from "@/pages/not-found";

/**
 * Router component that defines the application routes.
 * Uses wouter for client-side routing.
 * 
 * @returns A React component rendering route switches
 */
function Router() {
  return (
    <Switch>
      <Route path="/" component={Chat} />
      {/* Fallback to 404 */}
      <Route component={NotFound} />
    </Switch>
  );
}

/**
 * Main application component that sets up providers and routing.
 * Wraps the application with QueryClientProvider, ThemeProvider, and TooltipProvider.
 * 
 * @returns A React component rendering the root application structure
 */
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
