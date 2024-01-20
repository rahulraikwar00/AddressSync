<script>
	import '../app.pcss';
</script>

<div class="h-screen flex-col items-center justify-center bg-amber-50">
	<span
		class="m-2 inline-block items-center justify-center rounded-full bg-amber-200 px-2 py-1 text-center text-xs font-semibold text-blue-800"
	>
		<span
			class="vibrating-dot mr-2 inline-flex items-center rounded-full bg-green-500 px-1 py-1 text-xs font-semibold text-white"
		>
			<!-- Your content goes here, if any -->
		</span>Demo Mode
	</span>

	<slot />
</div>

<style>
	@keyframes vibrate {
		0% {
			opacity: 0%;
		}
		
		50% {
			opacity: 75%;
		}
		100% {
			opacity: 0%;
		}
	}

	.vibrating-dot {
		animation: vibrate 1s infinite; /* Adjust duration and other properties as needed */
	}
</style>
