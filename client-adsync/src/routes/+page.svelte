<script>
	import demo from '$lib/images/demo.png';
	import Icon from '@iconify/svelte';
</script>

<div class="flex-grow">
	<div class="relative isolate flex-grow px-6 pt-10 lg:px-8 lg:pt-16">
		<div
			class="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80"
			aria-hidden="true"
		>
			<div
				class="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
			></div>
		</div>
		<div class="sm:py-30 mx-auto max-w-2xl py-20 text-center">
			<div class="mb-8 flex items-center justify-center">
				<div
					class="block rounded-full px-3 py-1 text-gray-600 ring-1 ring-gray-900/10 hover:ring-gray-900/20 sm:hidden"
				>
					Major update coming soon! <a
						href="https://github.com/rahulraikwar00/AddressSync"
						class="font-semibold text-indigo-600"
						><span class="absolute inset-0" aria-hidden="true"></span> Stay tuned</a
					>
				</div>
				<div
					class="hidden px-3 py-1 text-gray-600 ring-1 ring-gray-900/10 hover:ring-gray-900/20 sm:relative sm:block sm:rounded-full sm:text-sm sm:leading-6"
				>
					Revolutionize your workflow with our upcoming major update! <a
						href="https://github.com/rahulraikwar00/AddressSync"
						class="font-semibold text-indigo-600"
						><span class="absolute inset-0" aria-hidden="true"></span> Stay tuned</a
					>
				</div>
			</div>
			<h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
				Simplify Address Management:<br class="hidden sm:inline" /><span class="text-purple-500"
					>Your Organization's Essential Solution</span
				>
			</h1>
			<p class="mt-6 text-lg leading-8 text-gray-600">
				Self-hosted, high-performance solution with automated database setup tailored to the
				specific needs, seamlessly integrated with Twilio for efficient communication.
			</p>
			<div class="mt-10 flex items-center justify-center gap-x-2">
				<a
					href="https://github.com/rahulraikwar00/AddressSync"
					class="flex items-center justify-between gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
				>
					<Icon icon="fa6-brands:github" width="20" height="20" />
					<span>Star on GitHub</span>
				</a>
				<a
					href="https://github.com/rahulraikwar00/AddressSync"
					class="flex items-center rounded-md bg-purple-600 px-3.5 py-2.5 text-sm font-medium text-white hover:bg-purple-700"
				>
					<span>Download</span>
					<Icon icon="fa-solid:download" width="20" height="20" class="ml-2" />
				</a>
			</div>
		</div>
	</div>
</div>
