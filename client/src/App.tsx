import { Route, Switch } from "wouter";
import { AppShell } from "@/components/layout";
import {
  DashboardPage,
  EvidencePage,
  ConversationsPage,
  SbvViewerPage,
  SettingsPage,
} from "@/pages";
import "./index.css";

function App() {
  return (
    <AppShell>
      <Switch>
        <Route path="/" component={DashboardPage} />
        <Route path="/evidence" component={EvidencePage} />
        <Route path="/conversations" component={ConversationsPage} />
        <Route path="/sbv" component={SbvViewerPage} />
        <Route path="/settings" component={SettingsPage} />
        <Route>
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-muted-foreground">404</h1>
              <p className="text-muted-foreground mt-2">Page not found</p>
              <a
                href="/"
                className="inline-block mt-4 text-primary underline hover:text-primary/80"
              >
                Go to Dashboard
              </a>
            </div>
          </div>
        </Route>
      </Switch>
    </AppShell>
  );
}

export default App;
