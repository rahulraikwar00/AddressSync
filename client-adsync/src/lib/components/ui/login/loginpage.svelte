<script lang="js">
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Label } from '$lib/components/ui/label';

	export let value;
	let checked = false;
</script>

<div class="flex h-screen w-full flex-col items-center justify-center">
	<Card.Root class="w-[350px] bg-teal-50  font-mono">
		<Card.Header class="flex flex-col justify-between gap-2">
			<Card.Title class=" text-2xl ">Welcome {value}</Card.Title>
			<Card.Description class="flex gap-2">
				<Checkbox id="terms" bind:checked />
				<Label
					for="terms"
					class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
				>
					I agree to allow the use of my Aadhaar details or KYC information.
				</Label>
			</Card.Description>
		</Card.Header>
		<Card.Content>
			<form>
				<div class="grid w-full items-center gap-4">
					<div class="flex flex-col space-y-1.5">
						<Button class="bg-teal-600 text-lg">Continue with Digilocker</Button>
					</div>
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
