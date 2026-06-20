import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import AppShell from '@/layout/AppShell'
import Dashboard from '@/pages/Dashboard'
import IncidentsList from '@/pages/IncidentsList'
import IncidentDetail from '@/pages/IncidentDetail'
import ChangeTimeline from '@/pages/ChangeTimeline'
import WeakRCAQueue from '@/pages/WeakRCAQueue'
import ServiceDependencyGraph from '@/pages/ServiceDependencyGraph'
import Services from '@/pages/Services'
import ChangeIntelligence from '@/pages/ChangeIntelligence'
import ChangeImpactPage from '@/pages/ChangeImpactPage'
import Analytics from '@/pages/Analytics'
import Settings from '@/pages/Settings'
import NotFound from '@/pages/NotFound'

function App() {
  return (
    <Router>
      <AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/incidents" element={<IncidentsList />} />
          <Route path="/incidents/:id" element={<IncidentDetail />} />
          <Route path="/incidents/:id/timeline" element={<ChangeTimeline />} />
          <Route path="/weak-rca-queue" element={<WeakRCAQueue />} />
          <Route path="/service-dependencies" element={<ServiceDependencyGraph />} />
          <Route path="/services" element={<Services />} />
          <Route path="/changes" element={<ChangeIntelligence />} />
          <Route path="/changes/:id/impact" element={<ChangeImpactPage />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AppShell>
    </Router>
  )
}

export default App
