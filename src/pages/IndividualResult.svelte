<script lang="ts">
  import { onMount } from 'svelte';
  import BarChart from '../components/BarChart.svelte';
  import { fly, fade, scale, slide } from 'svelte/transition';
  import { elasticOut, quintOut, backOut } from 'svelte/easing';

  interface Props {
    submissionId: string;
  }

  let { submissionId }: Props = $props();

  let result = $state<any>(null);
  let loading = $state(true);
  let error = $state('');
  let mounted = $state(false);

  onMount(() => {
    mounted = true;
    loadResult();
  });

  // Format a UTC/DB timestamp into India Standard Time
  function formatIST(dateStr: string): string {
    try {
      const normalized = /([zZ]|[+\-]\d{2}:\d{2})$/.test(dateStr) ? dateStr : `${dateStr}Z`;
      const s = new Date(normalized).toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric', month: 'short', day: '2-digit',
        hour: '2-digit', minute: '2-digit', hour12: true,
        timeZoneName: 'short'
      });
      return s.replace(' am', ' AM').replace(' pm', ' PM');
    } catch {
      return dateStr;
    }
  }

  // Keys we expect from detailed_scores for hackathon criteria
  const hackathonKeys = [
    { label: 'Productivity', key: 'productivity_justification' },
    { label: 'Out of the box thinking', key: 'out_of_box_thinking' },
    { label: 'Problem-solving skills', key: 'problem_solving_skills' },
    { label: 'Creativity', key: 'creativity_justification' },
    { label: 'Research capabilities', key: 'research_capabilities' },
    { label: 'Understanding the business', key: 'business_understanding' },
    { label: 'Use of non-famous tools', key: 'non_famous_tools_usage' }
  ];

  async function loadResult() {
    try {
      loading = true;
      error = '';
      
      console.log('Loading result for submission ID:', submissionId);
      const response = await fetch(`/api/results/${submissionId}`);
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        throw new Error(`Failed to load result: ${response.status} ${errorText}`);
      }
      
      result = await response.json();
      console.log('Loaded result:', result);
    } catch (err: any) {
      error = err.message || 'Failed to load result';
      console.error('Error loading result:', err);
    } finally {
      loading = false;
    }
  }

  function goBack() {
    window.location.hash = '/';
  }

  function viewAllResults() {
    window.location.hash = '/results';
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 overflow-hidden">
  {#if mounted}
    <header 
      class="bg-white shadow-md backdrop-blur-sm bg-opacity-95"
      in:fly={{ y: -50, duration: 600, easing: quintOut }}
    >
      <div class="max-w-5xl mx-auto px-6 py-6">
        <div class="flex justify-between items-center">
          <div>
            <h1 
              class="text-4xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-gradient"
              style="background-size: 200% auto;"
            >
              📊 Project Evaluation Results
            </h1>
            <p 
              class="mt-2 text-gray-600"
              in:fade={{ delay: 200, duration: 400 }}
            >
              Detailed AI-powered analysis and scoring
            </p>
          </div>
          <div class="flex gap-3">
            <button 
              onclick={goBack}
              class="px-5 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform"
              in:scale={{ delay: 300, duration: 400, easing: elasticOut }}
            >
              ← Back to Upload
            </button>
            <button 
              onclick={viewAllResults}
              class="px-5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform"
              in:scale={{ delay: 400, duration: 400, easing: elasticOut }}
            >
              📋 All Results
            </button>
          </div>
        </div>
      </div>
    </header>
  {/if}

  <main class="max-w-5xl mx-auto px-6 py-12">
    {#if error}
      <div
        class="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-lg flex items-start gap-3"
        in:slide={{ duration: 300 }}
      >
        <span class="text-2xl">❌</span>
        <div>
          <p class="font-semibold">Error Loading Result</p>
          <p>{error}</p>
          <p class="text-sm mt-2">Submission ID: {submissionId}</p>
          <div class="mt-4 space-x-4">
            <button 
              onclick={goBack}
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200"
            >
              ← Back to Upload
            </button>
            <button 
              onclick={viewAllResults}
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors duration-200"
            >
              View All Results
            </button>
          </div>
        </div>
      </div>
    {/if}

    {#if loading}
      <div 
        class="text-center py-12"
        in:fade={{ duration: 400 }}
      >
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p class="mt-4 text-gray-600">Loading evaluation results...</p>
      </div>
    {:else if result}
      <div 
        class="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow duration-300"
        in:fly={{ y: 50, duration: 600, delay: 200, easing: quintOut }}
      >
        <!-- Project Info -->
        <div class="mb-8 text-center">
          <h2 class="text-3xl font-bold text-gray-900 mb-2">{result.project_name}</h2>
          <p class="text-gray-600">{result.project_description}</p>
          <div class="mt-4 flex justify-center items-center gap-4">
            <span class="text-sm text-gray-500">Team: {result.team_name}</span>
            <span class="text-sm text-gray-500">•</span>
            <span class="text-sm text-gray-500">Evaluated: {formatIST(result.evaluation.evaluated_at)}</span>
          </div>
        </div>

        <!-- Overall Score -->
        <div 
          class="text-center mb-8 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl"
          in:scale={{ delay: 400, duration: 500, easing: backOut }}
        >
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Overall Score</h3>
          <div class="text-5xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            {result.evaluation.overall_score.toFixed(1)}/10
          </div>
        </div>

        <!-- Score Breakdown (Bars only for clarity and accessibility) -->
        <div class="mb-2"></div>

        <!-- Bar Charts -->
        <div 
          class="bg-gray-50 rounded-lg p-6 mb-8"
          in:fly={{ y: 20, delay: 1100, duration: 400 }}
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-4">📈 Detailed Scores</h3>
          <div class="space-y-4">
            <div in:fly={{ x: -20, delay: 1200, duration: 300 }}>
              <BarChart score={result.evaluation.relevance_score} label="Relevance" />
            </div>
            <div in:fly={{ x: -20, delay: 1300, duration: 300 }}>
              <BarChart score={result.evaluation.technical_complexity_score} label="Technical Complexity" />
            </div>
            <div in:fly={{ x: -20, delay: 1400, duration: 300 }}>
              <BarChart score={result.evaluation.creativity_score} label="Creativity" />
            </div>
            <div in:fly={{ x: -20, delay: 1500, duration: 300 }}>
              <BarChart score={result.evaluation.documentation_score} label="Documentation" />
            </div>
            <div in:fly={{ x: -20, delay: 1600, duration: 300 }}>
              <BarChart score={result.evaluation.productivity_score} label="Productivity" />
            </div>
          </div>
        </div>

        <!-- Hackathon Key Points (before feedback) -->
        {#if result.evaluation.detailed_scores}
        <div 
          class="bg-white rounded-xl p-6 shadow-lg border-2 border-indigo-50 mb-8"
          in:fly={{ y: 16, delay: 1550, duration: 350 }}
        >
          <h3 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            📚 Hackathon Key Points
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each hackathonKeys as item, i}
              {#if result.evaluation.detailed_scores[item.key]}
                <div class="bg-gradient-to-r from-slate-50 to-white rounded-lg p-4 shadow-sm border-l-4 border-indigo-400" in:fly={{ x: -12, delay: 1560 + i*90, duration: 250 }}>
                  <div class="text-sm text-gray-500 mb-1">{item.label}</div>
                  <div class="text-gray-700">{result.evaluation.detailed_scores[item.key]}</div>
                </div>
              {/if}
            {/each}
          </div>
        </div>
        {/if}

        <!-- AI Feedback -->
        <div 
          class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 shadow-lg mb-8"
          in:scale={{ delay: 1700, duration: 400, easing: elasticOut }}
        >
          <h3 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            🤖 AI Evaluation Feedback
          </h3>
          <div class="bg-white rounded-lg p-5 shadow-inner border-l-4 border-indigo-500">
            <p class="text-gray-700 leading-relaxed whitespace-pre-wrap">{result.evaluation.feedback}</p>
          </div>
        </div>

        <!-- Detailed Justifications -->
        {#if result.evaluation.detailed_scores && typeof result.evaluation.detailed_scores === 'object' && Object.keys(result.evaluation.detailed_scores).length > 0}
          <div 
            class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 shadow-lg mb-8"
            in:scale={{ delay: 1800, duration: 400, easing: elasticOut }}
          >
            <h3 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              📋 Detailed Score Justifications
            </h3>
            <div class="space-y-4">
              {#each Object.entries(result.evaluation.detailed_scores) as [key, value], i}
                <div 
                  class="bg-white rounded-lg p-4 shadow-sm border-l-4 border-purple-400"
                  in:fly={{ x: -20, delay: 1900 + (i * 100), duration: 300 }}
                >
                  <h4 class="font-semibold text-gray-800 capitalize mb-2 text-lg">
                    {key.replace('_justification', '').replace('_', ' ')}
                  </h4>
                  <p class="text-gray-600">{value}</p>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Enhanced Action Buttons -->
        <div 
          class="mt-12 flex flex-col sm:flex-row gap-6 justify-center items-center"
          in:scale={{ delay: 2000, duration: 400, easing: elasticOut }}
        >
          <button
            onclick={goBack}
            class="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-lg font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform flex items-center justify-center gap-3"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            🚀 Evaluate Another Project
          </button>
          
          <button
            onclick={viewAllResults}
            class="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-pink-600 to-red-600 text-white text-lg font-bold rounded-xl hover:from-pink-700 hover:to-red-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform flex items-center justify-center gap-3"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            🏆 View Leaderboard
          </button>
        </div>
      </div>
    {/if}
  </main>
</div>

<style>
  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  
  .animate-gradient {
    animation: gradient 3s ease infinite;
  }
</style>
