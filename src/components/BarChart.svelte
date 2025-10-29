<script lang="ts">
  interface Props {
    score: number;
    label: string;
    maxScore?: number;
    color?: string;
  }

  let { score, label, maxScore = 10, color }: Props = $props();
  
  const percentage = (score / maxScore) * 100;
  
  // Color scheme based on score
  const getColor = (s: number) => {
    if (color) return color;
    if (s >= 8) return 'bg-green-500';
    if (s >= 6) return 'bg-blue-500';
    if (s >= 4) return 'bg-orange-500';
    return 'bg-red-500';
  };
  
  const barColor = getColor(score);
</script>

<div class="space-y-2">
  <div class="flex justify-between items-center">
    <span class="text-sm font-semibold text-gray-700">{label}</span>
    <span class="text-sm font-bold text-gray-900">{score.toFixed(1)} / {maxScore}</span>
  </div>
  
  <div class="relative h-8 bg-gray-200 rounded-full overflow-hidden">
    <div 
      class="{barColor} h-full rounded-full transition-all duration-1000 ease-out flex items-center justify-end pr-3"
      style="width: {percentage}%"
    >
      {#if percentage > 15}
        <span class="text-xs font-semibold text-white">
          {percentage.toFixed(0)}%
        </span>
      {/if}
    </div>
  </div>
</div>

