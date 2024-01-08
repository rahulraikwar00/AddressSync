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

<div class="flex h-screen w-full flex-col items-center justify-center font-mono">
	<Card.Root class="w-[350px] shadow-sm">
		<Card.Header class="flex flex-col justify-between gap-2">
			<Card.Title class="self-center text-3xl">Login As {$curretUser}</Card.Title>
			<Card.Description class="flex gap-2 self-center"
				>Make sure to enter valid {$curretUser === 'Requester'
					? 'Aadhaar Number'
					: 'Organization Id'}</Card.Description
			>
		</Card.Header>
		<Card.Content>
			<form>
				<div class="grid w-full items-center gap-4">
					<div class="grid w-full max-w-sm items-center gap-1.5">
						<Label for="email"
							>{$curretUser === 'Requester' ? 'Aadhaar Number' : 'Organization Id'}</Label
						>
						<Input
							class="bg-input"

							type="email"
							id="email"
							placeholder={$curretUser === 'Requester' ? '1111-2222-3333' : 'ABc123'}
						/>
					</div>

					{#if !($curretUser === 'Requester')}
						<div class="grid w-full max-w-sm items-center gap-1.5">
							<Label for="password">Password</Label>
							<Input type="password" id="password" placeholder="*********" class="bg-input" />

						</div>
					{/if}
					{#if $curretUser === 'Requester'}
						<div>
							<Checkbox id="terms" />
							<Label for="terms">
								I agree to allow the use of my Aadhaar details for KYC information.
							</Label>
						</div>
					{/if}
					<div class="flex flex-col space-y-1.5">
						<Button class="text-lg "
							>{$curretUser === 'Accepter'
								? 'Continue With credentials'
								: 'Continue with Digilocker'}</Button
						>
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
