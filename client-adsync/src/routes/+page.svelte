<script lang="js">
	import LoginCard from '$lib/components/ui/login/loginCard.svelte';
	import Herotext from '$lib/components/ui/hero/herotext.svelte';
	import { onMount } from 'svelte';
	onMount(() => {
		console.log('home mounted!');
	});
</script>

<div >
	<div class="flex h-screen flex-col items-center justify-center lg:grid lg:grid-cols-5">
		<section class="col-span-3 p-6 text-center">
			<Herotext></Herotext>
		</section>

		<section class="col-span-2">
			<!-- Assuming LoginCard is a custIom component or element -->
			<LoginCard></LoginCard>
		</section>
	</div>
</div>
