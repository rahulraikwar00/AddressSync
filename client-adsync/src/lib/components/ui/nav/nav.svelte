<script>
	let open = false;

	function toggleMenu() {
		open = !open;
	}
</script>

<nav class="flex items-center justify-between bg-gray-800 p-4 text-white">
	<a href="/" class="text-xl font-bold">Your Logo</a>
	<button class="text-2xl focus:outline-none lg:hidden" on:click={toggleMenu}>&/9776;</button>

	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div
		class="fixed inset-0 z-50 bg-gray-800 bg-opacity-75 lg:hidden"
		class:show={open}
		on:click={() => (open = false)}
	>
		<div class="flex justify-end">
			<button class="text-2xl focus:outline-none" on:click={() => (open = false)}>&times;</button>
		</div>

		<div class="mt-4 space-y-4">
			<a href="/" class="block px-4 py-2 text-white hover:text-gray-300">Home</a>
			<a href="/" class="block px-4 py-2 text-white hover:text-gray-300">About</a>
			<a href="/" class="block px-4 py-2 text-white hover:text-gray-300">Services</a>
			<a href="/" class="block px-4 py-2 text-white hover:text-gray-300">Contact</a>
		</div>
	</div>
</nav>

<main class="container mx-auto p-8">
	<h1 class="text-4xl font-bold text-gray-800">Your Hero Content</h1>
	<p class="text-lg text-gray-600">A description of your awesome website.</p>
</main>
