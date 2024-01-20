<!-- Login.svelte -->
<script context="module" lang="ts">
	import { Toaster } from 'svelte-french-toast';
	import Button from '../button/button.svelte';
	import Label from '../label/label.svelte';
	import { isButtonDisabled, loginWithDigilocker, loginWithEmail } from './login';
	import { DoubleArrowRight, EnvelopeOpen } from 'radix-icons-svelte';
	import Input from '../input/input.svelte';
</script>

<div>
	<form class="flex flex-col items-center justify-center">
		<Toaster />
		<Label class="mb-8 block text-4xl font-semibold text-slate-800 lg:text-6xl lg:font-bold "
			>Log in</Label
		>
		<Button
			bind:disabled={$isButtonDisabled}
			class="mb-1 w-full max-w-xs "
			type="submit"
			on:click={() => {
				loginWithDigilocker();
			}}
		>
			<DoubleArrowRight class="mr-2 h-4 w-4" />
			Continue with Digilocker
		</Button>
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
				loginWithEmail();
			}}
			class="mb-5 w-full max-w-xs"
		>
			<EnvelopeOpen class="mr-2 h-4 w-4" />
			Magic link
		</Button>
		<!-- svelte-ignore a11y-missing-attribute -->
		<Label class="max-w-xs text-sm font-light text-slate-600"
			>Signing up signifies that you have read and agree to the <a
				class="cursor-pointer font-mono text-blue-500 underline">Terms of Service</a
			>
			and
			<a class="cursor-pointer font-mono text-blue-500 underline"> our Privacy Policy</a>. Cookie
			Preferences.
		</Label>
	</form>
</div>
