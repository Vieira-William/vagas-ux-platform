import { useState } from 'react';
import Dashboard from './components/Dashboard';
import LoadingScreen from './components/LoadingScreen';

function App() {
  const [isLoading, setIsLoading] = useState(true);

  if (isLoading) {
    return (
      <LoadingScreen
        onComplete={() => setIsLoading(false)}
      />
    );
  }

  return <Dashboard />;
}

export default App;
