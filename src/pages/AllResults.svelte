<script lang="ts">
  import { onMount } from 'svelte';
  import { fly, fade, scale, slide } from 'svelte/transition';
  import { elasticOut, quintOut, backOut } from 'svelte/easing';

  let allResults = $state<any[]>([]);
  let loading = $state(false);
  let error = $state('');
  let mounted = $state(false);
  let selectedResult = $state<any>(null);
  let showFeedbackModal = $state(false);

  onMount(() => {
    mounted = true;
    loadAllResults();
  });

  async function loadAllResults() {
    try {
      loading = true;
      error = '';
      
      // Get all hackathons first
      const hackathonsResponse = await fetch('/api/hackathons');
      if (!hackathonsResponse.ok) {
        throw new Error('Failed to load hackathons');
      }
      const hackathons = await hackathonsResponse.json();
      
      // Get submissions for each hackathon
      const allSubmissions = [];
      for (const hackathon of hackathons) {
        try {
          const submissionsResponse = await fetch(`/api/hackathon/${hackathon.id}/submissions`);
          if (submissionsResponse.ok) {
            const submissions = await submissionsResponse.json();
            // Add hackathon info to each submission
            submissions.forEach(submission => {
              submission.hackathon = hackathon;
            });
            allSubmissions.push(...submissions);
          }
        } catch (err) {
          console.warn(`Failed to load submissions for hackathon ${hackathon.id}:`, err);
        }
      }
      
      // Filter only evaluated submissions and sort by most recent first
      allResults = allSubmissions
        .filter(submission => submission.evaluated && submission.evaluation)
        .sort((a, b) => new Date(b.evaluation.evaluated_at).getTime() - new Date(a.evaluation.evaluated_at).getTime());
      
    } catch (err: any) {
      error = err.message || 'Failed to load results';
      console.error('Error loading results:', err);
    } finally {
      loading = false;
    }
  }

  function viewResult(submissionId: number) {
    window.location.hash = `/result/${submissionId}`;
  }

  function showFeedback(result: any, event: Event) {
    event.stopPropagation(); // Prevent the row click
    selectedResult = result;
    showFeedbackModal = true;
  }

  function closeFeedbackModal() {
    showFeedbackModal = false;
    selectedResult = null;
  }

  function goToUpload() {
    window.location.hash = '/';
  }

  // Format a UTC/DB timestamp into India Standard Time
  function formatIST(dateStr: string): string {
    try {
      // Treat missing timezone as UTC
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

  function getMedalEmoji(rank: number): string {
    if (rank === 0) return '🥇';
    if (rank === 1) return '🥈';
    if (rank === 2) return '🥉';
    return '🏅';
  }

  function getScoreColor(score: number): string {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-blue-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-red-600';
  }

  function getScoreBgColor(score: number): string {
    if (score >= 8) return 'bg-green-100';
    if (score >= 6) return 'bg-blue-100';
    if (score >= 4) return 'bg-yellow-100';
    return 'bg-red-100';
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 overflow-hidden">
  {#if mounted}
    <header 
      class="bg-white shadow-md backdrop-blur-sm bg-opacity-95"
      in:fly={{ y: -50, duration: 600, easing: quintOut }}
    >
      <div class="max-w-6xl mx-auto px-6 py-6">
        <div class="flex justify-between items-center">
          <div>
            <h1 
              class="text-4xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-gradient"
              style="background-size: 200% auto;"
            >
              🏆 All Evaluation Results
            </h1>
            <p 
              class="mt-2 text-gray-600"
              in:fade={{ delay: 200, duration: 400 }}
            >
              Leaderboard of all evaluated projects
            </p>
          </div>
          <button 
            onclick={goToUpload}
            class="px-5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform"
            in:scale={{ delay: 300, duration: 400, easing: elasticOut }}
          >
            ➕ Upload New Project
          </button>
        </div>
      </div>
    </header>
  {/if}

  <main class="max-w-6xl mx-auto px-6 py-12">
    {#if error}
      <div 
        class="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-lg flex items-start gap-3"
        in:slide={{ duration: 300 }}
      >
        <span class="text-2xl">❌</span>
        <div>
          <p class="font-semibold">Error</p>
          <p>{error}</p>
        </div>
      </div>
    {/if}

    {#if loading}
      <div 
        class="text-center py-12"
        in:fade={{ duration: 400 }}
      >
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p class="mt-4 text-gray-600">Loading all evaluation results...</p>
      </div>
    {:else if allResults.length === 0}
      <div 
        class="text-center py-12"
        in:fade={{ duration: 400 }}
      >
        <div class="text-6xl mb-4">📊</div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">No Results Yet</h2>
        <p class="text-gray-600 mb-6">No projects have been evaluated yet. Upload your first project to get started!</p>
        <button
          onclick={goToUpload}
          class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform"
        >
          🚀 Upload First Project
        </button>
      </div>
    {:else}
      <div 
        class="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow duration-300"
        in:fly={{ y: 50, duration: 600, delay: 200, easing: quintOut }}
      >
        <div class="mb-6">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">📋 Evaluation Leaderboard</h2>
          <p class="text-gray-600">Total Projects Evaluated: {allResults.length}</p>
        </div>

        <div class="space-y-4">
          {#each allResults as result, index}
            <div 
              class="border border-gray-200 rounded-lg p-6 hover:border-indigo-300 hover:shadow-lg transition-all duration-300"
              in:fly={{ x: -20, duration: 400, delay: index * 100 }}
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                  <!-- Rank -->
                  <div class="text-3xl">
                    {getMedalEmoji(index)}
                  </div>
                  
                  <!-- Project Info -->
                  <div 
                    class="cursor-pointer hover:text-indigo-600 transition-colors duration-200"
                    onclick={() => viewResult(result.id)}
                    title="Click to view detailed analysis"
                  >
                    <h3 class="text-xl font-semibold text-gray-900 hover:text-indigo-600">{result.project_name}</h3>
                    <p class="text-xs text-gray-500 mt-1">
                      Evaluated: {formatIST(result.evaluation.evaluated_at)}
                    </p>
                  </div>
                </div>

                <!-- Scores -->
                <div class="flex items-center gap-6">
                  <!-- Overall Score -->
                  <div class="text-center">
                    <div class="text-2xl font-bold {getScoreColor(result.evaluation.overall_score)} px-4 py-2 rounded-lg {getScoreBgColor(result.evaluation.overall_score)}">
                      {result.evaluation.overall_score.toFixed(1)}
                    </div>
                    <div class="text-xs text-gray-500 mt-1">Overall</div>
                  </div>

                  <!-- Feedback Button -->
                  <button 
                    onclick={(e) => showFeedback(result, e)}
                    class="text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 p-2 rounded-lg transition-all duration-200"
                    title="View AI Feedback"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Project Description -->
              {#if result.project_description}
                <div class="mt-3 text-sm text-gray-600 line-clamp-2">
                  {result.project_description}
                </div>
              {/if}
            </div>
          {/each}
        </div>

        <!-- Action Buttons -->
        <div class="mt-8 text-center">
          <button
            onclick={goToUpload}
            class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform"
          >
            🚀 Upload Another Project
          </button>
        </div>
      </div>
    {/if}
  </main>
</div>

<!-- Feedback Modal -->
{#if showFeedbackModal && selectedResult}
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    onclick={closeFeedbackModal}
    in:fade={{ duration: 200 }}
    out:fade={{ duration: 200 }}
  >
    <div 
      class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
      onclick={(e) => e.stopPropagation()}
      in:scale={{ duration: 300, easing: elasticOut }}
      out:scale={{ duration: 200 }}
    >
      <!-- Modal Header -->
      <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">{selectedResult.project_name}</h2>
            <p class="text-sm text-gray-600">AI Evaluation Feedback</p>
          </div>
          <button 
            onclick={closeFeedbackModal}
            class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-lg transition-all duration-200"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Modal Content -->
      <div class="p-6">
        <!-- Project Info -->
        <div class="mb-6 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-medium text-gray-700">Team: {selectedResult.team_name}</span>
            <span class="text-sm text-gray-500">Evaluated: {formatIST(selectedResult.evaluation.evaluated_at)}</span>
          </div>
          {#if selectedResult.project_description}
            <p class="text-sm text-gray-600">{selectedResult.project_description}</p>
          {/if}
        </div>

        <!-- Overall Score -->
        <div class="text-center mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Overall Score</h3>
          <div class="text-4xl font-bold {getScoreColor(selectedResult.evaluation.overall_score)}">
            {selectedResult.evaluation.overall_score.toFixed(1)}/10
          </div>
        </div>

        <!-- Score Breakdown -->
        <div class="grid grid-cols-5 gap-4 mb-6">
          <div class="text-center p-3 bg-gray-50 rounded-lg">
            <div class="text-lg font-bold {getScoreColor(selectedResult.evaluation.relevance_score)}">
              {selectedResult.evaluation.relevance_score.toFixed(1)}
            </div>
            <div class="text-xs text-gray-600">Relevance</div>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded-lg">
            <div class="text-lg font-bold {getScoreColor(selectedResult.evaluation.technical_complexity_score)}">
              {selectedResult.evaluation.technical_complexity_score.toFixed(1)}
            </div>
            <div class="text-xs text-gray-600">Technical</div>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded-lg">
            <div class="text-lg font-bold {getScoreColor(selectedResult.evaluation.creativity_score)}">
              {selectedResult.evaluation.creativity_score.toFixed(1)}
            </div>
            <div class="text-xs text-gray-600">Creativity</div>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded-lg">
            <div class="text-lg font-bold {getScoreColor(selectedResult.evaluation.documentation_score)}">
              {selectedResult.evaluation.documentation_score.toFixed(1)}
            </div>
            <div class="text-xs text-gray-600">Documentation</div>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded-lg">
            <div class="text-lg font-bold {getScoreColor(selectedResult.evaluation.productivity_score)}">
              {selectedResult.evaluation.productivity_score.toFixed(1)}
            </div>
            <div class="text-xs text-gray-600">Productivity</div>
          </div>
        </div>

        <!-- AI Feedback -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            🤖 AI Generated Feedback
          </h3>
          <div class="prose prose-sm max-w-none">
            <p class="text-gray-700 leading-relaxed whitespace-pre-wrap">{selectedResult.evaluation.feedback}</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="mt-6 flex justify-center gap-4">
          <button
            onclick={() => viewResult(selectedResult.id)}
            class="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform"
          >
            📊 View Detailed Analysis
          </button>
          <button
            onclick={closeFeedbackModal}
            class="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  @keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  
  .animate-gradient {
    animation: gradient 3s ease infinite;
  }

  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
