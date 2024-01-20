import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
import toast from 'svelte-french-toast';
import { user } from '$lib/stores';

interface user {
	usernmae: string;
}

export const isButtonDisabled = writable(false);

// Function to toggle the disabled state
export function toggleDisabledState() {
	// Update the store value to toggle between true and false
	isButtonDisabled.update((value) => !value);
}

export function loginWithDigilocker() {
	toast.promise(
		new Promise((resolve) => {
			toggleDisabledState();
			// Simulate an asynchronous operation, like saving settings
			setTimeout(() => {
				resolve('promise resolve');
				toggleDisabledState();
			}, 1000); // Adjust the timeout as needed
		})
			.then(() => {
				user.set('Demo user');
				goto('/dashboard');
			})
			.catch(() => {
				goto('/');
			}),
		{
			loading: 'loading...',
			success: 'Welcome Back!',
			error: 'Failed try again!'
		}
	);
}

export function loginWithEmail() {
	toast.promise(
		new Promise((resolve) => {
			toggleDisabledState();
			// Simulate an asynchronous operation, like saving settings
			setTimeout(() => {
				resolve('promise resolve');
				toggleDisabledState();
			}, 1000); // Adjust the timeout as needed
		}),
		{
			loading: 'loading...',
			success: 'Success! Check your email for login credentials!',
			error: 'Failed try again!'
		}
	);
}
