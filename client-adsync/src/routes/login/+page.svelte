<script>
	import { goto } from '$app/navigation';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Label } from '$lib/components/ui/label';
	import { curretUser } from '$lib/components/ui/stores.js';
	import { onMount } from 'svelte';
	import { Input } from '$lib/components/ui/input';
	onMount(() => {
		if ($curretUser === 'User') {
			goto('/');
		}
	});
</script>

<div class="flex h-screen w-full flex-col items-center justify-center">
	<Card.Root class="w-[400px] shadow-sm">
		<Card.Header class="flex flex-col justify-between gap-2">
			<Card.Title class="mb-0 self-center text-3xl">Login As {$curretUser}</Card.Title>
			<Card.Description class="mt-0 flex gap-2 self-center"
				>Make sure to enter valid aadhaar number</Card.Description>
		</Card.Header>
		<Card.Content>
			<form>
				<div class="grid w-full items-center gap-4">
					<div class="grid w-full max-w-sm items-center gap-1.5">
						<Label for="email">Aadhaar Number</Label>
						<Input type="email" id="email" placeholder="1111-2222-3333" />
					</div>
					<div>
						<Checkbox id="terms" />
						<Label
							for="terms"
							class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
						>
							I agree to allow the use of my Aadhaar details for KYC information.
						</Label>
					</div>
					<div class="flex flex-col space-y-1.5">
						<Button class="text-lg hover:bg-teal-600">Continue with Digilocker</Button>
					<div class="mb-4 flex items-center gap-4"></div>
				</div>
			</form>
		</Card.Content>
		<Card.Footer class="flex justify-between">
			<Label
				>If not registered <a
					href="https://www.digilocker.gov.in/"
					target="_blank"
					class="underline hover:text-blue-500">click</a
				> here</Label
			>
		</Card.Footer>
	</Card.Root>
</div>
