// Simple hash-based router for Svelte 5
import { writable } from 'svelte/store';

function getPath() {
  return window.location.hash.slice(1) || '/';
}

function createRouter() {
  const { subscribe, set } = writable(getPath());

  window.addEventListener('hashchange', () => {
    set(getPath());
  });

  return {
    subscribe,
    navigate: (path: string) => {
      window.location.hash = path;
    }
  };
}

export const currentPath = createRouter();

