import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { useTheme } from '../context/ThemeContext'

export default function CommunityChart({ communities = [] }) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const textColor = isDark ? '#99A0B4' : '#747770'
  const tooltipBg = isDark ? '#171D2B' : '#FFFFFF'
  const tooltipBorder = isDark ? '#2A3344' : '#E3E4DF'

  const cellColors = [
    isDark ? '#9B93FF' : '#635BFF',
    isDark ? '#72DBEF' : '#0088A8',
    isDark ? '#F5B041' : '#D48207',
    isDark ? '#79D8AD' : '#1F9E66',
  ]

  const chartData = communities.map((c, idx) => ({
    name: `Cell ${c.community_id}`,
    label: c.label,
    size: c.size,
    color: cellColors[idx % cellColors.length],
  }))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload
      return (
        <div
          className="p-3 rounded-card text-xs shadow-card"
          style={{ backgroundColor: tooltipBg, border: `1px solid ${tooltipBorder}` }}
        >
          <span className="font-semibold text-primary block">{item.label}</span>
          <div className="mt-1 flex items-center justify-between gap-4 text-xs font-mono">
            <span className="text-secondary">Member Entities:</span>
            <span className="font-bold text-accent-violet">{item.size}</span>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 15, right: 20, left: -10, bottom: 5 }}>
          <XAxis
            dataKey="name"
            stroke={textColor}
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke={textColor}
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="size" radius={[6, 6, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
