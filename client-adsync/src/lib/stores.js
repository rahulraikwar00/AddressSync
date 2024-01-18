import { writable } from 'svelte/store';

export const curretUser = writable('User');
// src/stores/user.js

export const user = writable(null);

// ... Repeat the pattern for other stores
