<script lang="js">
	import { curretUser } from '$lib/components/ui/stores.js';
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import img from '$lib/images/hero2.png';

	function handleClick(data) {
		curretUser.set(data);
		goto('/login');
		console.log(data);
	}
</script>

<section
	class="container flex flex-col gap-4 pb-12 pt-4 text-center lg:items-center lg:gap-8 lg:py-20"
>
	<div class="flex max-w-3xl flex-col items-center justify-center text-center">
		<h1 class="mb-10 text-4xl font-bold md:text-5xl xl:text-6xl dark:text-white">
			Welcome to Address Syncing Service
		</h1>
		<p class="text-md mb-6 max-w-2xl font-mono lg:mb-8 lg:text-xl dark:text-gray-400">
			"Experience seamless address updates with ADSync's powerful features. Securely sync,
			lightning-fast processing, and revolutionize your address management."
		</p>

		<div class="flex justify-center gap-2">
			<Button on:click={() => handleClick('Requester')} class=" text-lg text-primary-foreground"
				>Requester</Button
			>
			<Button on:click={() => handleClick('Accepter')} class="text-lg text-primary-foreground"
				>Accepter</Button
			>
		</div>

		<p class="text-md mb-6 mt-4 max-w-2xl font-mono lg:mb-8 lg:text-lg">
			Join <a href="/" class="font-bold underline">Adsync</a> and elevate your address management experience.
			Welcome to a world of secure, fast, and efficient syncing.
		</p>

	</div>
</section>
