import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import AppShell from './layout/AppShell'
import Dashboard from './pages/Dashboard'
import IncidentsList from './pages/IncidentsList'
import IncidentDetail from './pages/IncidentDetail'
import WeakRCAQueue from './pages/WeakRCAQueue'
import ServiceDependencyGraph from './pages/ServiceDependencyGraph'
import Services from './pages/Services'
import ChangeIntelligence from './pages/ChangeIntelligence'
import AutonomousActions from './pages/AutonomousActions'
import Analytics from './pages/Analytics'
import KnowledgeBase from './pages/KnowledgeBase'
import Settings from './pages/Settings'

function App() {
  return (
    <Router>
      <AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/incidents" element={<IncidentsList />} />
          <Route path="/incidents/:id" element={<IncidentDetail />} />
          <Route path="/weak-rca-queue" element={<WeakRCAQueue />} />
          <Route path="/service-dependencies" element={<ServiceDependencyGraph />} />
          <Route path="/services" element={<Services />} />
          <Route path="/changes" element={<ChangeIntelligence />} />
          <Route path="/autonomous-actions" element={<AutonomousActions />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/knowledge-base" element={<KnowledgeBase />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </AppShell>
    </Router>
  )
}

export default App
