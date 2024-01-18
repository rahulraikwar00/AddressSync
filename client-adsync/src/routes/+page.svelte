<script lang="js">
	import { Button } from '$lib/components/ui/button';
	import Input from '$lib/components/ui/input/input.svelte';
	import Label from '$lib/components/ui/label/label.svelte';

	import { EnvelopeOpen, DoubleArrowRight } from 'radix-icons-svelte';
	import { onMount } from 'svelte';
	import toast, { Toaster } from 'svelte-french-toast';

	onMount(() => {
		console.log('home mounted!');
	});

	function loginWithEmail(props) {
		if (props === 'Email') {
			toast.success('Please check your Email for login Credentials!', {
				duration: 2000
			});
		} else {
			toast.success('Login successfull!');
		}
	}

	function loginWithDigilocker(params) {
		console.log('emmai', params);
	}
</script>

<div class="grid h-screen grid-cols-2 items-center justify-center sm:grid-flow-col sm:grid-cols-2">
	<Toaster />
	<section class="col-span-1 p-6 text-center">
		<h1 class="mb-4 text-4xl font-bold text-gray-800">About Our Service</h1>
	</section>

	<section class="col-span-1">
		<div class="">
			<form class="flex flex-col items-center justify-center">
				<Label class="mb-6 text-6xl font-bold  ">Log in</Label>
				<Button
					class="mb-1 w-full max-w-xs"
					tyep="submit"
					on:click={() => {
						loginWithDigilocker('digilocker');
					}}
				>
					<DoubleArrowRight class="mr-2 h-4 w-4" />
					Continue with Digilocker</Button
				>
				<p class="mb-1 text-center text-gray-600">
					If not registered, <a href="/" class="text-blue-500">click here</a>
				</p>
			</form>

			<form class=" mt-4 flex flex-col items-center justify-center">
				<Label for="email" class="sr-only">Email</Label>
				<Input type="email" placeholder="email" class="mb-1 max-w-xs" />
				<Button
					on:click={() => {
						loginWithEmail('Email');
					}}
					variant="outline"
					class="w-full max-w-xs"
				>
					<EnvelopeOpen class="mr-2 h-4 w-4" />
					Login with Email
				</Button>
			</form>
		</div>
	</section>
</div>
