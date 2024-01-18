import { writable } from 'svelte/store';

export const curretUser = writable('User');
// src/stores/user.js
import { writable } from 'svelte/store';

export const user = writable(null);

// src/stores/addressFormData.js
import { writable } from 'svelte/store';

export const addressFormData = writable({
	fullName: '',
	currentAddress: '',
	newAddress: '',
	contactInformation: '',
	additionalDetails: ''
});

// src/stores/notifications.js
import { writable } from 'svelte/store';

export const notifications = writable([]);

// ... Repeat the pattern for other stores
