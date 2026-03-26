<script>
	import Footer from '$lib/component/footer.svelte';
	import '../app.pcss';
	import Header from '$lib/component/header.svelte';
</script>

<div class=" flex min-h-screen flex-col justify-between">
	<Header />
	<slot />
	<Footer />
</div>
