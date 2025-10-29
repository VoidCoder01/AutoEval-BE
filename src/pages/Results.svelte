<script lang="ts">
  import { onMount } from 'svelte';
  import { hackathonApi, evaluationApi, type Hackathon } from '../lib/api';
  import RadialChart from '../components/RadialChart.svelte';
  import BarChart from '../components/BarChart.svelte';
  import { fly, fade, scale, slide } from 'svelte/transition';
  import { elasticOut, quintOut, backOut } from 'svelte/easing';

  interface Props {
    hackathonId?: string;
  }

  let { hackathonId }: Props = $props();

  let hackathons = $state<Hackathon[]>([]);
  let selectedHackathonId = $state<number | null>(hackathonId ? parseInt(hackathonId) : null);
  let selectedHackathon = $state<Hackathon | null>(null);
  let results = $state<any[]>([]);
  let loading = $state(false);
  let error = $state('');
  let expandedResultId = $state<number | null>(null);
  let mounted = $state(false);

  onMount(() => {
    mounted = true;
  });

  onMount(async () => {
    await loadHackathons();
    if (selectedHackathonId) {
      await loadResults();
    }
  });

  async function loadHackathons() {
    try {
      loading = true;
      error = '';
      hackathons = await hackathonApi.getAll();
      if (selectedHackathonId) {
        selectedHackathon = hackathons.find(h => h.id === selectedHackathonId) || null;
      }
    } catch (err: any) {
      error = err.message || 'Failed to load hackathons';
      console.error('Error loading hackathons:', err);
    } finally {
      loading = false;
    }
  }

  async function loadResults() {
    if (!selectedHackathonId) return;

    try {
      loading = true;
      error = '';
      results = await evaluationApi.getByHackathon(selectedHackathonId);
      selectedHackathon = hackathons.find(h => h.id === selectedHackathonId) || null;
      
      // Sort by overall score
      results.sort((a, b) => (b.evaluation?.overall_score || 0) - (a.evaluation?.overall_score || 0));
    } catch (err: any) {
      error = err.message || 'Failed to load results';
      console.error('Error loading results:', err);
    } finally {
      loading = false;
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

  function getScoreBarColor(score: number): string {
    if (score >= 8) return 'bg-green-500';
    if (score >= 6) return 'bg-blue-500';
    if (score >= 4) return 'bg-yellow-500';
    return 'bg-red-500';
  }

  function toggleDetails(resultId: number) {
    expandedResultId = expandedResultId === resultId ? null : resultId;
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100">
  <!-- Header -->
  <header class="bg-white shadow">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">🏆 Leaderboard & Results</h1>
          <p class="mt-1 text-sm text-gray-500">View AI evaluation results and rankings</p>
        </div>
        <div class="flex gap-3">
          <a href="#/" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition">
            Dashboard
          </a>
          <a href="#/submit" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition">
            Submit Project
          </a>
        </div>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {#if error}
      <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-800">{error}</p>
      </div>
    {/if}

    <!-- Hackathon Selector -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <label for="hackathon-select" class="block text-sm font-medium text-gray-700 mb-3">
        Select Hackathon
      </label>
      {#if loading && hackathons.length === 0}
        <div class="text-gray-500">Loading...</div>
      {:else if hackathons.length === 0}
        <p class="text-gray-500">No hackathons found</p>
      {:else}
        <select
          id="hackathon-select"
          bind:value={selectedHackathonId}
          onchange={loadResults}
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value={null}>Choose a hackathon...</option>
          {#each hackathons as hackathon}
            <option value={hackathon.id}>{hackathon.name}</option>
          {/each}
        </select>
      {/if}
    </div>

    {#if !selectedHackathonId}
      <div class="bg-white rounded-lg shadow p-12 text-center">
        <div class="text-6xl mb-4">🎯</div>
        <h3 class="text-xl font-semibold text-gray-700 mb-2">Select a Hackathon</h3>
        <p class="text-gray-500">Choose a hackathon to view its evaluation results and leaderboard</p>
      </div>
    {:else}
      <!-- Hackathon Info -->
      {#if selectedHackathon}
        <div class="bg-gradient-to-r from-primary-600 to-indigo-600 rounded-lg shadow-lg p-6 mb-6 text-white">
          <h2 class="text-2xl font-bold mb-2">{selectedHackathon.name}</h2>
          <p class="text-primary-100">{selectedHackathon.description}</p>
          <div class="mt-4 flex items-center gap-4 text-sm">
            <span>📊 {results.length} Submissions</span>
            <span>📅 Created: {new Date(selectedHackathon.created_at || '').toLocaleDateString()}</span>
          </div>
        </div>
      {/if}

      <!-- Results Table -->
      {#if loading}
        <div class="bg-white rounded-lg shadow p-12 text-center">
          <div class="text-gray-500">Loading results...</div>
        </div>
      {:else if results.length === 0}
        <div class="bg-white rounded-lg shadow p-12 text-center">
          <div class="text-6xl mb-4">📭</div>
          <h3 class="text-xl font-semibold text-gray-700 mb-2">No Results Yet</h3>
          <p class="text-gray-500">Submissions are still being evaluated or no submissions have been made.</p>
        </div>
      {:else}
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <!-- Summary Stats -->
          <div class="p-6 bg-gray-50 border-b border-gray-200">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="text-center">
                <div class="text-3xl font-bold text-primary-600">
                  {results.filter(r => r.evaluation).length}
                </div>
                <div class="text-sm text-gray-600">Evaluated</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-green-600">
                  {(results.reduce((acc, r) => acc + (r.evaluation?.overall_score || 0), 0) / results.filter(r => r.evaluation).length).toFixed(1)}
                </div>
                <div class="text-sm text-gray-600">Avg Score</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-blue-600">
                  {Math.max(...results.map(r => r.evaluation?.overall_score || 0)).toFixed(1)}
                </div>
                <div class="text-sm text-gray-600">Highest</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-yellow-600">
                  {results.filter(r => !r.evaluation).length}
                </div>
                <div class="text-sm text-gray-600">Pending</div>
              </div>
            </div>
          </div>

          <!-- Leaderboard -->
          <div class="p-6">
            <h3 class="text-lg font-semibold mb-4">🏆 Rankings</h3>
            <div class="space-y-4">
              {#each results as result, index}
                {@const evaluation = result.evaluation}
                <div class="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition {index < 3 ? 'bg-gradient-to-r from-yellow-50 to-orange-50' : ''}">
                  <div class="flex items-start gap-4">
                    <!-- Rank -->
                    <div class="flex-shrink-0 text-center">
                      <div class="text-3xl">{getMedalEmoji(index)}</div>
                      <div class="text-sm font-semibold text-gray-600 mt-1">#{index + 1}</div>
                    </div>

                    <!-- Project Info -->
                    <div class="flex-1">
                      <div class="flex justify-between items-start mb-3">
                        <div>
                          <h4 class="text-lg font-bold text-gray-900">{result.project_name}</h4>
                          <p class="text-sm text-gray-600">Team: {result.team_name}</p>
                        </div>
                        {#if evaluation}
                          <div class="text-right">
                            <div class="text-3xl font-bold {getScoreColor(evaluation.overall_score)}">
                              {evaluation.overall_score.toFixed(1)}
                            </div>
                            <div class="text-xs text-gray-500">/ 10</div>
                          </div>
                        {:else}
                          <span class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                            ⏳ Evaluating...
                          </span>
                        {/if}
                      </div>

                      {#if evaluation}
                        <!-- Score Breakdown -->
                        <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-3">
                          <div>
                            <div class="text-xs text-gray-600 mb-1">Relevance</div>
                            <div class="flex items-center gap-2">
                              <div class="flex-1 bg-gray-200 rounded-full h-2">
                                <div class="{getScoreBarColor(evaluation.relevance_score)} h-2 rounded-full" style="width: {evaluation.relevance_score * 10}%"></div>
                              </div>
                              <span class="text-sm font-semibold {getScoreColor(evaluation.relevance_score)}">
                                {evaluation.relevance_score.toFixed(1)}
                              </span>
                            </div>
                          </div>

                          <div>
                            <div class="text-xs text-gray-600 mb-1">Technical</div>
                            <div class="flex items-center gap-2">
                              <div class="flex-1 bg-gray-200 rounded-full h-2">
                                <div class="{getScoreBarColor(evaluation.technical_complexity_score)} h-2 rounded-full" style="width: {evaluation.technical_complexity_score * 10}%"></div>
                              </div>
                              <span class="text-sm font-semibold {getScoreColor(evaluation.technical_complexity_score)}">
                                {evaluation.technical_complexity_score.toFixed(1)}
                              </span>
                            </div>
                          </div>

                          <div>
                            <div class="text-xs text-gray-600 mb-1">Creativity</div>
                            <div class="flex items-center gap-2">
                              <div class="flex-1 bg-gray-200 rounded-full h-2">
                                <div class="{getScoreBarColor(evaluation.creativity_score)} h-2 rounded-full" style="width: {evaluation.creativity_score * 10}%"></div>
                              </div>
                              <span class="text-sm font-semibold {getScoreColor(evaluation.creativity_score)}">
                                {evaluation.creativity_score.toFixed(1)}
                              </span>
                            </div>
                          </div>

                          <div>
                            <div class="text-xs text-gray-600 mb-1">Documentation</div>
                            <div class="flex items-center gap-2">
                              <div class="flex-1 bg-gray-200 rounded-full h-2">
                                <div class="{getScoreBarColor(evaluation.documentation_score)} h-2 rounded-full" style="width: {evaluation.documentation_score * 10}%"></div>
                              </div>
                              <span class="text-sm font-semibold {getScoreColor(evaluation.documentation_score)}">
                                {evaluation.documentation_score.toFixed(1)}
                              </span>
                            </div>
                          </div>

                          <div>
                            <div class="text-xs text-gray-600 mb-1">Productivity</div>
                            <div class="flex items-center gap-2">
                              <div class="flex-1 bg-gray-200 rounded-full h-2">
                                <div class="{getScoreBarColor(evaluation.productivity_score)} h-2 rounded-full" style="width: {evaluation.productivity_score * 10}%"></div>
                              </div>
                              <span class="text-sm font-semibold {getScoreColor(evaluation.productivity_score)}">
                                {evaluation.productivity_score.toFixed(1)}
                              </span>
                            </div>
                          </div>
                        </div>

                        <!-- View Details Button -->
                        <button
                          onclick={() => toggleDetails(result.id)}
                          class="mt-4 w-full px-4 py-2 bg-gradient-to-r from-primary-600 to-indigo-600 text-white rounded-lg hover:from-primary-700 hover:to-indigo-700 transition flex items-center justify-center gap-2"
                        >
                          {#if expandedResultId === result.id}
                            📊 Hide Detailed Analysis
                          {:else}
                            📊 View Detailed Analysis with Charts
                          {/if}
                        </button>

                        <!-- Expanded Detailed View -->
                        {#if expandedResultId === result.id}
                          <div 
                            class="mt-6 p-6 bg-gradient-to-br from-gray-50 to-blue-50 rounded-lg border-2 border-primary-200"
                            in:slide={{ duration: 400, easing: quintOut }}
                          >
                            <h4 
                              class="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2"
                              in:fade={{ delay: 100, duration: 300 }}
                            >
                              📊 Detailed Score Analysis
                            </h4>

                            <!-- Radial Charts -->
                            <div class="grid grid-cols-2 md:grid-cols-5 gap-6 mb-6">
                              <div in:scale={{ delay: 200, duration: 500, easing: backOut }}>
                                <RadialChart score={evaluation.relevance_score} label="Relevance" />
                              </div>
                              <div in:scale={{ delay: 300, duration: 500, easing: backOut }}>
                                <RadialChart score={evaluation.technical_complexity_score} label="Technical" />
                              </div>
                              <div in:scale={{ delay: 400, duration: 500, easing: backOut }}>
                                <RadialChart score={evaluation.creativity_score} label="Creativity" />
                              </div>
                              <div in:scale={{ delay: 500, duration: 500, easing: backOut }}>
                                <RadialChart score={evaluation.documentation_score} label="Documentation" />
                              </div>
                              <div in:scale={{ delay: 600, duration: 500, easing: backOut }}>
                                <RadialChart score={evaluation.productivity_score} label="Productivity" />
                              </div>
                            </div>

                            <!-- Bar Charts -->
                            <div 
                              class="bg-white rounded-lg p-6 shadow-sm mb-6"
                              in:fly={{ y: 20, delay: 700, duration: 400 }}
                            >
                              <h5 class="text-md font-semibold text-gray-900 mb-4">📈 Score Breakdown</h5>
                              <div class="space-y-4">
                                <div in:fly={{ x: -20, delay: 800, duration: 300 }}>
                                  <BarChart score={evaluation.relevance_score} label="Relevance" />
                                </div>
                                <div in:fly={{ x: -20, delay: 900, duration: 300 }}>
                                  <BarChart score={evaluation.technical_complexity_score} label="Technical Complexity" />
                                </div>
                                <div in:fly={{ x: -20, delay: 1000, duration: 300 }}>
                                  <BarChart score={evaluation.creativity_score} label="Creativity" />
                                </div>
                                <div in:fly={{ x: -20, delay: 1100, duration: 300 }}>
                                  <BarChart score={evaluation.documentation_score} label="Documentation" />
                                </div>
                                <div in:fly={{ x: -20, delay: 1200, duration: 300 }}>
                                  <BarChart score={evaluation.productivity_score} label="Productivity" />
                                </div>
                              </div>
                            </div>

                            <!-- AI Feedback -->
                            <div 
                              class="bg-white rounded-lg p-6 shadow-sm"
                              in:scale={{ delay: 1300, duration: 400, easing: elasticOut }}
                            >
                              <h5 class="text-md font-semibold text-gray-900 mb-3 flex items-center gap-2">
                                💬 AI Evaluation Feedback
                              </h5>
                              <p class="text-sm text-gray-700 leading-relaxed">{evaluation.feedback}</p>
                            </div>
                          </div>
                        {/if}
                      {/if}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </main>
</div>

