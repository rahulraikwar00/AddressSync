<script>
	import { page } from '$app/stores';
	import '../app.pcss';
</script>

<section class="flex h-screen w-full flex-col items-center justify-center bg-white">
	<div>
		<h1 class="uppercase tracking-widest text-gray-500">{$page.status} | {$page.error.message}</h1>
	</div>
</section>
