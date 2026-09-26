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

export default function CentralityChart({ data = [], metric = 'betweenness' }) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const textColor = isDark ? '#99A0B4' : '#747770'
  const primaryBar = isDark ? '#9B93FF' : '#635BFF'
  const tooltipBg = isDark ? '#171D2B' : '#FFFFFF'
  const tooltipBorder = isDark ? '#2A3344' : '#E3E4DF'

  const formattedData = data.slice(0, 8).map(d => ({
    name: d.name.length > 15 ? `${d.name.substring(0, 15)}...` : d.name,
    fullName: d.name,
    role: d.role,
    score: d.score,
    id: d.id,
  }))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload
      return (
        <div
          className="p-3 rounded-card text-xs shadow-card"
          style={{ backgroundColor: tooltipBg, border: `1px solid ${tooltipBorder}` }}
        >
          <span className="font-semibold text-primary block">{item.fullName}</span>
          {item.role && <span className="text-secondary text-[11px] block">{item.role}</span>}
          <div className="mt-1.5 flex items-center justify-between gap-4 text-xs font-mono">
            <span className="text-secondary uppercase">{metric}:</span>
            <span className="font-bold text-accent-violet">{item.score}</span>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={formattedData}
          layout="vertical"
          margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
        >
          <XAxis
            type="number"
            stroke={textColor}
            fontSize={11}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            stroke={textColor}
            fontSize={11}
            tickLine={false}
            axisLine={false}
            width={110}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="score" radius={[0, 4, 4, 0]} fill={primaryBar}>
            {formattedData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={index === 0 ? (isDark ? '#FF9A7B' : '#E85D3F') : primaryBar}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
