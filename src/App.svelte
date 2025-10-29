<script lang="ts">
  import { currentPath } from './lib/router';
  import ProjectEvaluator from './pages/ProjectEvaluator.svelte';
  import AllResults from './pages/AllResults.svelte';
  import IndividualResult from './pages/IndividualResult.svelte';
  import { onMount } from 'svelte';

  let path = $state('/');
  let submissionId = $state<string | undefined>(undefined);

  // Robustly subscribe to router changes (works in Svelte 5 runes)
  onMount(() => {
    const unsubscribe = currentPath.subscribe((p: string) => {
      path = p;

      // Parse submission ID from path like /result/123
      const resultMatch = p.match(/^\/result\/(\d+)$/);
      if (resultMatch) {
        submissionId = resultMatch[1];
        path = '/result';
      } else {
        submissionId = undefined;
      }
    });
    return () => unsubscribe();
  });
</script>

{#if path === '/results'}
  <AllResults />
{:else if path === '/result' && submissionId}
  <IndividualResult {submissionId} />
{:else}
  <ProjectEvaluator />
{/if}
