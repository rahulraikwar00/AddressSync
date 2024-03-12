<script>
	import Icon from '@iconify/svelte';

</script>

<div class=" flex flex-col justify-between min-h-screen">
	<nav class="flex justify-between bg-purple-100 m-1 rounded-md md:px-20">
		<ul class=" flex justify-items-start gap-3 px-2 m-2">
			<li>
				<span class="flex gap-1 pr-4">
					<Icon icon="fluent-emoji-high-contrast:rabbit-face" width="40" height="40" />
				</span>
			</li>
			<li class="text-gray-600 hover:text-gray-900 py-2">
				<a href="/Docs">Docs</a>
			</li>
			<li class="text-gray-600 hover:text-gray-900 py-2">
				<a href="https://github.com/rahulraikwar00/AddressSync">Github</a>
			</li>
		</ul>
		<ul class="flex justify-end m-2 px-2">
			<li class="hover:bg-purple-300 hover:rounded-full py-2 px-1">
				<Icon icon="devicon:github" width="25" height="25" />
			</li>
			<li class="hover:bg-purple-300 hover:rounded- py-2 px-1">
				<Icon icon="fa6-brands:x-twitter" width="25" height="25" />
			</li>
		</ul>
	</nav>
	<div class="relative isolate px-6 pt-10 lg:px-8 lg:pt-5">
		<div
			class="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80"
			aria-hidden="true"
		>
			<div
				class="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]"
				style="clip-path: polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)"
			></div>
		</div>
		<div class="mx-auto max-w-2xl py-20 sm:py-30">
			<div class=" mb-8 flex justify-center items-center md">
				<div
					class="relative rounded-full px-3 py-1 text-sm leading-6 text-gray-600 ring-1 ring-gray-900/10 hover:ring-gray-900/20"
				>
					Major update for address sync is <a href="https://github.com/rahulraikwar00/AddressSync" class="font-semibold text-indigo-600"
						><span class="absolute inset-0" aria-hidden="true"></span>coming soon
					</a>
				</div>
			</div>
			<div class="text-center">
				<h1 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-5xl">
					<span class="underline decoration-purple-400"> Simplify Address Management: </span>
					Your Organization's Essential Solution
				</h1>
				<p class="mt-6 text-md md:text-lg leading-8 text-gray-600">
					Self-hosted, high-performance solution with automated database setup tailored to the
					specific needs, seamlessly integrated with Twilio for efficient communication.
				</p>
				<div class="mt-10 flex items-center justify-center gap-x-2">
					<!-- svelte-ignore a11y-invalid-attribute -->
					<a
						href="https://github.com/rahulraikwar00/AddressSync"
						class=" border rounded-lg px-3 py-2.5 gap-2 flex justify-between gap-2text-sm font-semibold leading-6 text-gray-900"
					>
						<Icon icon="fa6-brands:github" width="25" height="25" />

						<span> Star on github </span>
					</a>
					<!-- svelte-ignore a11y-invalid-attribute -->
					<a
						href="https://github.com/rahulraikwar00/AddressSync"
						class=" rounded-md flex bg-purple-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-purple-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
						>Download</a
					>
				</div>
			</div>
		</div>

		<div
			class="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]"
			aria-hidden="true"
		>
			<div
				class="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%+36rem)] sm:w-[72.1875rem]"
				style="clip-path: polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)"
			></div>
		</div>
	</div>

	<div class=" bg-purple-100 py-4">
		<div class="flex justify-center items-center gap-6 p-3">
			<Icon icon="fa6-brands:x-twitter" width="25" height="25" />
			<Icon icon="fa6-brands:google" width="25" height="25" />
			<Icon icon="fa6-brands:linkedin" width="25" height="25" />
			<Icon icon="fa6-brands:instagram" width="25" height="25" />
			<Icon icon="fa6-brands:github   " width="25" height="25" />
		</div>
		<div class="flex justify-center items-center">
			<p>&copy; 2024 <a href="https://www.lunosis.xyz">Lunosis</a>. All rights reserved.</p>
		</div>
	</div>
</div>
