import { ChevronRight, Save } from 'lucide-react'

const sections = [
  {
    title: 'Integrations',
    description: 'Configure data sources and alert channels',
    items: ['Datadog', 'New Relic', 'Prometheus', 'CloudWatch'],
  },
  {
    title: 'AI Configuration',
    description: 'Customize AI analysis parameters',
    items: ['Model Selection', 'Confidence Thresholds', 'Analysis Depth', 'Hypothesis Generation'],
  },
  {
    title: 'Notifications',
    description: 'Manage alerts and escalation policies',
    items: ['Alert Rules', 'Escalation Policies', 'Notification Channels', 'On-Call Schedule'],
  },
  {
    title: 'Security & Access',
    description: 'Manage permissions and credentials',
    items: ['RBAC Settings', 'API Keys', 'OAuth Providers', 'Audit Logs'],
  },
]

export default function Settings() {
  return (
    <div className="p-8 max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Settings</h1>
        <p className="text-muted-foreground">Configure platform integrations, AI settings, and security</p>
      </div>

      <div className="space-y-4">
        {sections.map((section, idx) => (
          <div key={idx} className="bg-card border border-border rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-foreground">{section.title}</h2>
                <p className="text-sm text-muted-foreground mt-1">{section.description}</p>
              </div>
              <ChevronRight size={20} className="text-muted-foreground" />
            </div>
            
            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-border">
              {section.items.map((item, itemIdx) => (
                <a
                  key={itemIdx}
                  href="#"
                  className="px-4 py-3 bg-background/50 hover:bg-background border border-border hover:border-primary rounded-lg text-sm text-muted-foreground hover:text-foreground transition-all text-center font-medium"
                >
                  {item}
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium">
          <Save size={18} />
          Save Changes
        </button>
      </div>
    </div>
  )
}
