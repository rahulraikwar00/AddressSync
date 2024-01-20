<script>
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';

	import * as Tabs from '$lib/components/ui/tabs';
	import { onMount } from 'svelte';
	import UnderConstruction from '$lib/components/ui/temp/under_construction.svelte';

	onMount(() => {
		if ($user === null) {
			goto('/');
		}
	});

	const requests = [
		{
			requestId: 'REQ001',
			organizationName: 'ABC Corp',
			orgId: 'ORG001',
			date: '2024-01-18',
			status: 'Approved'
		},
		{
			requestId: 'REQ002',
			organizationName: 'XYZ Ltd',
			orgId: 'ORG002',
			date: '2024-01-19',
			status: 'Pending'
		},
		{
			requestId: 'REQ003',
			organizationName: '123 Inc',
			orgId: 'ORG003',
			date: '2024-01-20',
			status: 'Rejected'
		},
		{
			requestId: 'REQ003',
			organizationName: '123 Inc',
			orgId: 'ORG003',
			date: '2024-01-20',
			status: 'Rejected'
		},
		{
			requestId: 'REQ003',
			organizationName: '123 Inc',
			orgId: 'ORG003',
			date: '2024-01-20',
			status: 'Rejected'
		},
		{
			requestId: 'REQ003',
			organizationName: '123 Inc',
			orgId: 'ORG003',
			date: '2024-01-20',
			status: 'Rejected'
		},
		{
			requestId: 'REQ003',
			organizationName: '123 Inc',
			orgId: 'ORG003',
			date: '2024-01-20',
			status: 'Rejected'
		}

		// Add more data as needed
	];

	function getStatusColor(status) {
		if (status === 'Approved') {
			return 'bg-green-200';
		} else if (status === 'Pending') {
			return 'bg-yellow-200';
		} else if (status === 'Rejected') {
			return 'bg-red-200';
		} else {
			return 'bg-gray-200';
		}
	}
</script>

<div class="flex flex-col items-center justify-center">
	<h1 class="my-5 text-2xl">Welcome {$user}</h1>

	<Tabs.Root value="Request-Status" class="items-center justify-center text-center w-5/6 lg:max-w-screen-md ">
		<Tabs.List>
			<Tabs.Trigger value="Request-Status">Request Status</Tabs.Trigger>
			<Tabs.Trigger value="Send-Request">Send Request</Tabs.Trigger>
		</Tabs.List>

		<Tabs.Content value="Request-Status" class="items-center justify-center  p-4 lg:w-full">
			{#each requests as items}
				<div
					class="min-w-sm mb-2 flex justify-around gap-1 rounded-lg p-2 shadow-md {getStatusColor(
						items.status
					)}"
				>
					<!-- Avatar div with circular styling -->
					<div class="flex h-8 w-8 items-center justify-center rounded-full bg-teal-400">
						<!-- You can place your image or avatar content here -->
						<span class="text-md text-white">👤</span>
					</div>

					<!-- Container for organization information -->
					<div class="flex flex-grow flex-col">
						<h1 class="mb-1 text-sm font-semibold">{items.organizationName}</h1>
						<p class="text-xs text-gray-700">{items.requestId}</p>
					</div>

					<!-- Status div -->
					<div class="flex items-center">
						<span class="text-sm text-gray-600">{items.status}</span>
					</div>
				</div>
			{/each}
		</Tabs.Content>

		<Tabs.Content value="Send-Request">
			<UnderConstruction></UnderConstruction>
		</Tabs.Content>
	</Tabs.Root>
</div>
