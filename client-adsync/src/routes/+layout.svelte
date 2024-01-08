<script>
	import Nav from '$lib/components/ui/nav/nav.svelte';
	import '../app.pcss';
</script>

<div class="h-screen flex-col items-center justify-center bg-green-100">
	<div class="fixed top-2 z-50 w-full">
		<Nav></Nav>
	</div>
	<div class="mt-16 w-full rounded-lg p-2">
		<slot />
	</div>
</div>
