import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const accuracyData = [
  { week: 'Week 1', accuracy: 78 },
  { week: 'Week 2', accuracy: 82 },
  { week: 'Week 3', accuracy: 85 },
  { week: 'Week 4', accuracy: 88 },
  { week: 'Week 5', accuracy: 91 },
]

const confidenceData = [
  { range: '90-100%', count: 24 },
  { range: '80-90%', count: 18 },
  { range: '70-80%', count: 12 },
  { range: '60-70%', count: 8 },
  { range: '<60%', count: 3 },
]

const throughputData = [
  { day: 'Mon', incidents: 12, analyzed: 11 },
  { day: 'Tue', incidents: 15, analyzed: 14 },
  { day: 'Wed', incidents: 10, analyzed: 10 },
  { day: 'Thu', incidents: 18, analyzed: 17 },
  { day: 'Fri', incidents: 14, analyzed: 13 },
  { day: 'Sat', incidents: 8, analyzed: 8 },
  { day: 'Sun', incidents: 6, analyzed: 6 },
]

export default function Analytics() {
  return (
    <div className="p-8 max-w-7xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Analytics</h1>
        <p className="text-muted-foreground">Operational intelligence and RCA performance metrics</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-card border border-border rounded-lg p-6">
          <p className="text-xs text-muted-foreground mb-2">RCA Accuracy (This Month)</p>
          <p className="text-3xl font-bold text-green-400">91%</p>
          <p className="text-xs text-muted-foreground mt-2">↑ 5% from last month</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-6">
          <p className="text-xs text-muted-foreground mb-2">Avg. Analysis Time</p>
          <p className="text-3xl font-bold text-blue-400">8.2m</p>
          <p className="text-xs text-muted-foreground mt-2">↓ 1.3m improvement</p>
        </div>
        <div className="bg-card border border-border rounded-lg p-6">
          <p className="text-xs text-muted-foreground mb-2">Autonomous Action Success</p>
          <p className="text-3xl font-bold text-purple-400">94%</p>
          <p className="text-xs text-muted-foreground mt-2">87 actions executed</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* RCA Accuracy Trend */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="font-semibold text-foreground mb-4">RCA Accuracy Trend</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={accuracyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="week" stroke="var(--muted-foreground)" />
              <YAxis stroke="var(--muted-foreground)" domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'hsl(var(--foreground))',
                }}
              />
              <Line type="monotone" dataKey="accuracy" stroke="#22c55e" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Confidence Distribution */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="font-semibold text-foreground mb-4">Confidence Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={confidenceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="range" stroke="var(--muted-foreground)" />
              <YAxis stroke="var(--muted-foreground)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'hsl(var(--foreground))',
                }}
              />
              <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Investigation Throughput */}
        <div className="bg-card border border-border rounded-lg p-6 col-span-2">
          <h3 className="font-semibold text-foreground mb-4">Investigation Throughput (Last 7 Days)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={throughputData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="day" stroke="var(--muted-foreground)" />
              <YAxis stroke="var(--muted-foreground)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'hsl(var(--foreground))',
                }}
              />
              <Legend />
              <Bar dataKey="incidents" fill="#ef4444" radius={[8, 8, 0, 0]} />
              <Bar dataKey="analyzed" fill="#22c55e" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
