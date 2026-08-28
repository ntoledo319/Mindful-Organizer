import { Component, type ReactNode } from 'react';
import { QueryErrorState } from './ui';

// Calm fallback when a screen crashes during render: navigation and the tray
// stay alive, and the user can retry the view in place. There is no crash
// reporter by design (no telemetry), so the trace stays in the local console.
export class ScreenErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: unknown) {
    console.error('[paulatim] screen render failed', error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <QueryErrorState
          title="This view stumbled"
          body="Nothing was sent anywhere. Your records are still on this device."
          onRetry={() => this.setState({ hasError: false })}
        />
      );
    }
    return this.props.children;
  }
}
