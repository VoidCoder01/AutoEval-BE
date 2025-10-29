<script lang="ts">
  interface Props {
    score: number;
    label: string;
    color?: string;
  }

  let { score, label, color = '#3b82f6' }: Props = $props();
  
  // Calculate percentage and circle properties
  const percentage = (score / 10) * 100;
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (percentage / 100) * circumference;
  
  // Color scheme based on score
  const getColor = (s: number) => {
    if (color !== '#3b82f6') return color;
    if (s >= 8) return '#10b981'; // Green
    if (s >= 6) return '#3b82f6'; // Blue
    if (s >= 4) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
  };
  
  const chartColor = getColor(score);
</script>

<div class="flex flex-col items-center">
  <svg class="transform -rotate-90" width="120" height="120">
    <!-- Background circle -->
    <circle
      cx="60"
      cy="60"
      r={radius}
      stroke="#e5e7eb"
      stroke-width="8"
      fill="none"
    />
    <!-- Progress circle -->
    <circle
      cx="60"
      cy="60"
      r={radius}
      stroke={chartColor}
      stroke-width="8"
      fill="none"
      stroke-dasharray={circumference}
      stroke-dashoffset={dashOffset}
      stroke-linecap="round"
      class="transition-all duration-1000 ease-out"
    />
    <!-- Center text -->
    <text
      x="60"
      y="60"
      text-anchor="middle"
      dy="7"
      class="transform rotate-90 origin-center text-2xl font-bold"
      fill={chartColor}
      style="transform-origin: 60px 60px;"
    >
      {score.toFixed(1)}
    </text>
  </svg>
  
  <div class="mt-3 text-center">
    <p class="text-sm font-semibold text-gray-700">{label}</p>
    <p class="text-xs text-gray-500">{percentage.toFixed(0)}%</p>
  </div>
</div>

