<script lang="ts">
  import { hackathonApi, submissionApi } from '../lib/api';
  import { fly, fade, scale, slide } from 'svelte/transition';
  import { elasticOut, quintOut } from 'svelte/easing';

  let projectName = $state('');
  let evaluationQuery = $state('Evaluate this project for technical quality, innovation, and best practices');
  let projectFiles = $state<FileList | null>(null);
  let uploading = $state(false);
  let error = $state('');
  let success = $state('');
  let evaluationId = $state<number | null>(null);

  let dragActive = $state(false);
  let mounted = $state(false);

  $effect(() => {
    mounted = true;
  });

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragActive = false;
    
    if (e.dataTransfer?.files) {
      projectFiles = e.dataTransfer.files;
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    dragActive = true;
  }

  function handleDragLeave() {
    dragActive = false;
  }

  function handleFileChange(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files) {
      projectFiles = target.files;
    }
  }

  async function evaluateProject() {
    if (!projectName.trim()) {
      error = 'Please enter a project name';
      return;
    }

    if (!projectFiles || projectFiles.length === 0) {
      error = 'Please upload at least one file';
      return;
    }

    try {
      uploading = true;
      error = '';
      success = '';

      // Create a temporary hackathon for this evaluation
      const hackathon = await hackathonApi.create({
        name: `Project: ${projectName}`,
        description: evaluationQuery,
        evaluation_prompt: evaluationQuery,
        host_email: 'host@autoeval.ai',
        deadline: ''
      });

      // Upload files as a submission
      const formData = new FormData();
      formData.append('hackathon_id', hackathon.id.toString());
      formData.append('team_name', 'Evaluation Team');
      formData.append('participant_email', 'participant@autoeval.ai');
      formData.append('project_name', projectName);
      formData.append('project_description', evaluationQuery);

      // Add all files
      for (let i = 0; i < projectFiles.length; i++) {
        formData.append('project_files', projectFiles[i]);
      }

      const response = await fetch('/api/submissions', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to upload project');
      }

              const submission = await response.json();
              evaluationId = submission.id;

              // Show brief success message then redirect
              success = `✅ Project evaluated successfully! Overall Score: ${submission.overall_score}/10`;
              console.log(`✅ Project evaluated successfully! Redirecting to result page...`);
              
              // Redirect after a brief moment to show success
              setTimeout(() => {
                window.location.hash = `/result/${submission.id}`;
              }, 1500);

    } catch (err: any) {
      error = err.message || 'Failed to evaluate project';
      console.error('Error evaluating project:', err);
    } finally {
      uploading = false;
    }
  }

  function clearFiles() {
    projectFiles = null;
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  }

  function getFileIcon(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    const icons: Record<string, string> = {
      'py': '🐍',
      'js': '📜',
      'ts': '📘',
      'html': '🌐',
      'css': '🎨',
      'json': '📋',
      'md': '📝',
      'txt': '📄',
      'zip': '📦',
      'pdf': '📕',
      'png': '🖼️',
      'jpg': '🖼️',
      'jpeg': '🖼️',
      'gif': '🖼️',
      'svg': '🎭'
    };
    return icons[ext || ''] || '📄';
  }

  function formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 overflow-hidden">
  <!-- Header -->
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
              🤖 EvalAI
            </h1>
            <p 
              class="mt-2 text-gray-600"
              in:fade={{ delay: 200, duration: 400 }}
            >
              Upload your project and get instant AI-powered evaluation
            </p>
          </div>
          <a 
            href="#/results" 
            class="px-5 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 transform"
            in:scale={{ delay: 300, duration: 400, easing: elasticOut }}
          >
            📊 View Results
          </a>
        </div>
      </div>
    </header>
  {/if}

  <main class="max-w-5xl mx-auto px-6 py-12">
    {#if error}
      <div 
        class="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-lg flex items-start gap-3"
        in:slide={{ duration: 300 }}
        out:fade={{ duration: 200 }}
      >
        <span class="text-2xl">❌</span>
        <div>
          <p class="font-semibold">Error</p>
          <p>{error}</p>
        </div>
      </div>
    {/if}

    {#if success}
      <div 
        class="mb-6 p-4 bg-green-50 border-l-4 border-green-500 text-green-700 rounded-lg flex items-start gap-3"
        in:scale={{ duration: 400, easing: elasticOut }}
        out:fade={{ duration: 200 }}
      >
        <span class="text-2xl animate-bounce">✅</span>
        <div>
          <p class="font-semibold">Success!</p>
          <p>{success}</p>
          <p class="text-sm mt-1 text-green-600">Redirecting to results page...</p>
        </div>
      </div>
    {/if}

    <!-- Evaluation Form -->
    {#if mounted}
      <div 
        class="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow duration-300"
        in:fly={{ y: 50, duration: 600, delay: 400, easing: quintOut }}
      >
      <div class="space-y-8">
        <!-- Project Name -->
        <div>
          <label for="project-name" class="block text-lg font-semibold text-gray-900 mb-3">
            📁 Project Name
          </label>
          <input
            id="project-name"
            type="text"
            bind:value={projectName}
            placeholder="e.g., AI Chatbot, E-commerce Platform, Portfolio Website"
            class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-lg transition"
            disabled={uploading}
          />
        </div>

        <!-- Evaluation Query -->
        <div>
          <label for="eval-query" class="block text-lg font-semibold text-gray-900 mb-3">
            🎯 Evaluation Criteria
          </label>
          <textarea
            id="eval-query"
            bind:value={evaluationQuery}
            placeholder="Describe what you want to evaluate... (e.g., 'Evaluate for an AI hackathon focusing on innovation and code quality')"
            rows="4"
            class="w-full px-5 py-4 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-lg transition resize-none"
            disabled={uploading}
          ></textarea>
          <p class="mt-2 text-sm text-gray-500">
            💡 Be specific! The AI will evaluate your project based on this criteria.
          </p>
        </div>

        <!-- File Upload Area -->
        <div>
          <label for="file-input" class="block text-lg font-semibold text-gray-900 mb-3">
            📤 Upload Project Files
          </label>
          
          <div
            role="button"
            tabindex="0"
            class="relative border-4 border-dashed rounded-xl transition-all duration-200 {dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-gray-50'}"
            ondrop={handleDrop}
            ondragover={handleDragOver}
            ondragleave={handleDragLeave}
          >
            <input
              id="file-input"
              type="file"
              multiple
              onchange={handleFileChange}
              class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={uploading}
              accept=".py,.js,.ts,.html,.css,.json,.md,.txt,.zip,.pdf,.png,.jpg,.jpeg,.gif,.svg,.java,.cpp,.c,.go,.rb,.php,.swift,.kt,.rs"
            />
            
            <div class="p-12 text-center">
              <div class="text-6xl mb-4">
                {#if dragActive}
                  📥
                {:else}
                  📦
                {/if}
              </div>
              <p class="text-xl font-semibold text-gray-700 mb-2">
                {#if dragActive}
                  Drop your files here!
                {:else}
                  Drag & drop files or click to browse
                {/if}
              </p>
              <p class="text-sm text-gray-500">
                Supports: Code files, docs, images, PDFs, ZIP archives
              </p>
              <p class="text-xs text-gray-400 mt-2">
                Max size: 50MB per file
              </p>
            </div>
          </div>

          <!-- Uploaded Files List -->
          {#if projectFiles && projectFiles.length > 0}
            <div class="mt-4 space-y-2">
              <div class="flex justify-between items-center mb-3">
                <p class="text-sm font-semibold text-gray-700">
                  📎 {projectFiles.length} file{projectFiles.length > 1 ? 's' : ''} selected
                </p>
                <button
                  onclick={clearFiles}
                  class="text-sm text-red-600 hover:text-red-700 font-medium"
                  disabled={uploading}
                >
                  Clear all
                </button>
              </div>
              
              <div class="max-h-64 overflow-y-auto space-y-2">
                {#each Array.from(projectFiles) as file, i}
                  <div 
                    class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all duration-200 hover:scale-102 hover:shadow-md"
                    in:fly={{ x: -20, duration: 300, delay: i * 50 }}
                  >
                    <span class="text-2xl">{getFileIcon(file.name)}</span>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                      <p class="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>

        <!-- Submit Button -->
        <div class="pt-4">
          <button
            onclick={evaluateProject}
            disabled={uploading || !projectName.trim() || !projectFiles || projectFiles.length === 0}
            class="w-full py-5 px-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xl font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            {#if uploading}
              <span class="flex items-center justify-center gap-3">
                <svg class="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Evaluating with AI...
              </span>
            {:else}
              🚀 Start AI Evaluation
            {/if}
          </button>
        </div>
      </div>
    </div>

    <!-- Info Cards -->
    <div class="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
      <div 
        class="bg-white rounded-xl p-6 shadow-lg border-2 border-indigo-100 hover:border-indigo-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 transform"
        in:scale={{ duration: 400, delay: 600, easing: elasticOut }}
      >
        <div class="text-4xl mb-3 animate-bounce">⚡</div>
        <h3 class="text-lg font-bold text-gray-900 mb-2">Instant Analysis</h3>
        <p class="text-sm text-gray-600">Get AI-powered evaluation results in seconds</p>
      </div>
      
      <div 
        class="bg-white rounded-xl p-6 shadow-lg border-2 border-purple-100 hover:border-purple-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 transform"
        in:scale={{ duration: 400, delay: 700, easing: elasticOut }}
      >
        <div class="text-4xl mb-3 animate-pulse">📊</div>
        <h3 class="text-lg font-bold text-gray-900 mb-2">5 Key Metrics</h3>
        <p class="text-sm text-gray-600">Relevance, Technical, Creativity, Documentation, Productivity</p>
      </div>
      
      <div 
        class="bg-white rounded-xl p-6 shadow-lg border-2 border-pink-100 hover:border-pink-300 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 transform"
        in:scale={{ duration: 400, delay: 800, easing: elasticOut }}
      >
        <div class="text-4xl mb-3">💡</div>
        <h3 class="text-lg font-bold text-gray-900 mb-2">AI Feedback</h3>
        <p class="text-sm text-gray-600">Detailed insights and improvement suggestions</p>
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

