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
<section class="bg-white dark:bg-gray-900">
	<div class="mx-auto grid max-w-screen-xl px-4 py-8 lg:grid-cols-12 lg:gap-8 lg:py-16 xl:gap-0 ">
		<div class="hidden lg:col-span-5 lg:mt-0 lg:flex">
			<!-- svelte-ignore a11y-img-redundant-alt -->
			<img class="h-auto max-w-full" src={img} alt="image description" />
		</div>
		<div class="mr-auto place-self-center lg:col-span-7">
			<h1
				class="mb-6 max-w-2xl text-6xl leading-none tracking-tight text-teal-600 md:text-5xl xl:text-6xl dark:text-white"
			>
				Welcome to Address Syncing Service
			</h1>
			<p class="mb-6 max-w-2xl text-gray-500 md:text-lg lg:mb-8 lg:text-xl dark:text-gray-400">
				"Experience seamless address updates with ADSync's powerful features. Securely sync,
				lightning-fast processing, and revolutionize your address management."
			</p>

			<!-- <h2 class="mb-4 text-2xl">Join now</h2> -->
			<div class="flex w-full gap-2 text-teal-600">
				<Button on:click={() => handleClick('Requester')} class="bg-teal-600 text-xl"
					>Requester</Button
				>
				<Button on:click={() => handleClick('Accepter')} class="bg-teal-600 text-xl"
					>Accepter</Button
				>
			</div>
			<p class="mb-6 mt-4 max-w-2xl text-gray-500 md:text-lg lg:mb-8 lg:text-lg dark:text-gray-400">
				Join <a href="/" class="font-extrabold underline">Adsync</a> and elevate your address management
				experience. Welcome to a world of secure, fast, and efficient syncing.
			</p>
		</div>
	</div>
</section>
