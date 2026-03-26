<script>
	import Icon from '@iconify/svelte';
</script>

<nav class="relative z-10 bg-white shadow-md">
	<div class="container mx-auto flex items-center justify-between px-4 py-2">
		<div class="flex items-center">
			<a href="/" class="flex items-center gap-1">
				<Icon
					icon="fluent-emoji-high-contrast:rabbit-face"
					width="40"
					height="40"
					class="text-purple-600"
				/>
				<span class="text-2xl font-bold text-purple-600">SYNCme</span>
			</a>
		</div>
		<div class="hidden items-center space-x-4 md:flex">
			<a href="/Docs" class="text-gray-600 hover:text-purple-600">Docs</a>
			<a href="/Features" class="text-gray-600 hover:text-purple-600">Features</a>
			<a href="/Pricing" class="text-gray-600 hover:text-purple-600">Pricing</a>
			<a href="/About" class="text-gray-600 hover:text-purple-600">About</a>
			<a href="/Contact" class="text-gray-600 hover:text-purple-600">Contact</a>
		</div>
		<div class="flex items-center space-x-2">
			<a
				href="https://github.com/rahulraikwar00/AddressSync"
				target="_blank"
				rel="noopener noreferrer"
				class="hover:text-gray-600"
			>
				<Icon icon="devicon:github" width="25" height="25" class="text-gray-600" />
			</a>
			<a
				href="https://twitter.com/rahulraikwar00"
				target="_blank"
				rel="noopener noreferrer"
				class="hover:text-gray-600"
			>
				<Icon icon="fa6-brands:x-twitter" width="25" height="25" class="text-gray-600" />
			</a>
			<button class="ml-4 rounded-full bg-purple-600 px-4 py-2 text-white hover:bg-purple-700">
				Download
			</button>
		</div>
	</div>
</nav>
