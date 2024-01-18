<script>
	import toast, { Toaster } from 'svelte-french-toast';
	import { Button } from '$lib/components/ui/button';
	import Input from '$lib/components/ui/input/input.svelte';
	import Label from '$lib/components/ui/label/label.svelte';
	import { EnvelopeOpen, DoubleArrowRight } from 'radix-icons-svelte';
	import { writable } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { error } from '@sveltejs/kit';

	const isButtonDisabled = writable(true);

	// Function to toggle the disabled state
	function toggleDisabledState() {
		// Update the store value to toggle between true and false
		isButtonDisabled.update((value) => !value);
	}

	function loginWithDigilocker(props) {
		toast.promise(
			new Promise((resolve, reject) => {
				toggleDisabledState();
				// Simulate an asynchronous operation, like saving settings
				setTimeout(() => {
					resolve('promise resolve');
					toggleDisabledState();
				}, 2000); // Adjust the timeout as needed
			})
				.then(() => {
					user.set('Demo user');
					goto('/dashboard');
				})
				.catch((error) => {
					goto('/');
				}),
			{
				loading: 'loading...',
				success: 'Welcome Back!',
				error: 'Failed try again!.'
			}
		);
	}
	function loginWithEmail() {
		toast.promise(
			new Promise((resolve, reject) => {
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
				error: 'Failed try again!.'
			}
		);
	}
</script>

<div>
	<form class="flex flex-col items-center justify-center">
		<Toaster></Toaster>
		<!-- svelte-ignore missing-declaration -->
		<Label class="mb-8 block text-4xl font-semibold text-slate-800 lg:text-6xl lg:font-bold "
			>Log in</Label
		>
		<Button
			bind:disabled={$isButtonDisabled}
			class="mb-1 w-full max-w-xs "
			tyep="submit"
			on:click={() => {
				loginWithDigilocker('digilocker');
			}}
		>
			<DoubleArrowRight class="mr-2 h-4 w-4" />
			Continue with Digilocker</Button
		>
		<p class="mb-1 text-center text-slate-600">
			If not registered, <a href="/" class="text-blue-500">click here</a>
		</p>
	</form>

	<form class=" mt-4 flex flex-col items-center justify-center">
		<Label for="email" class="sr-only">Email</Label>
		<Input type="email" placeholder="Enter Your Aadhaar Linked Email" class="mb-2 max-w-xs" />
		<Button
			bind:disabled={$isButtonDisabled}
			on:click={() => {
				loginWithEmail('Email');
			}}
			class="w-full max-w-xs"
		>
			<EnvelopeOpen class="mr-2 h-4 w-4" />
			Magic link
		</Button>
	</form>
</div>
