document.addEventListener("DOMContentLoaded", () => {
	const spinner = document.getElementById("spinnerOverlay");
	const stateSelect = document.getElementById("state");
	const citySelect = document.getElementById("city");

	const states = [
		"Andhra Pradesh",
		"Arunachal Pradesh",
		"Assam",
		"Bihar",
		"Chhattisgarh",
		"Goa",
		"Gujarat",
		"Haryana",
		"Himachal Pradesh",
		"Jharkhand",
		"Karnataka",
		"Kerala",
		"Madhya Pradesh",
		"Maharashtra",
		"Manipur",
		"Meghalaya",
		"Mizoram",
		"Nagaland",
		"Odisha",
		"Punjab",
		"Rajasthan",
		"Sikkim",
		"Tamil Nadu",
		"Telangana",
		"Tripura",
		"Uttar Pradesh",
		"Uttarakhand",
		"West Bengal",
		"Delhi",
		"Jammu and Kashmir",
		"Ladakh",
	];

	states.forEach((state) => {
		const option = document.createElement("option");
		option.value = state;
		option.textContent = state;
		stateSelect.appendChild(option);
	});

	async function fetchCities(state) {
		try {
			spinner.style.display = "flex";
			const cached = localStorage.getItem(`cities_${state}`);
			if (cached) {
				console.log(`Loading cities for ${state} from cache`);
				spinner.style.display = "none";
				return JSON.parse(cached);
			}
			console.log(`Fetching cities for ${state}...`);
			const controller = new AbortController();
			const timeout = setTimeout(() => controller.abort(), 30000);
			const res = await fetch(
				"https://countriesnow.space/api/v0.1/countries/state/cities",
				{
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ country: "India", state }),
					signal: controller.signal,
				},
			);
			clearTimeout(timeout);
			const data = await res.json();
			if (!data.data) throw new Error("Invalid cities data");
			localStorage.setItem(`cities_${state}`, JSON.stringify(data.data));
			spinner.style.display = "none";
			console.log(`Fetched ${data.data.length} cities for ${state}`);
			return data.data;
		} catch (err) {
			console.error(`Failed to fetch cities for ${state}:`, err);
			spinner.style.display = "none";
			alert(`Failed to load cities for ${state}`);
			return [];
		}
	}

	stateSelect.addEventListener("change", async function () {
		const state = this.value;
		citySelect.innerHTML = '<option value="">Select City</option>';
		if (!state) return;
		const cities = await fetchCities(state);
		cities.forEach((city) => {
			const option = document.createElement("option");
			option.value = city;
			option.textContent = city;
			citySelect.appendChild(option);
		});
	});

	const form = document.getElementById("feasibilityForm");
	form.addEventListener("submit", async function (e) {
		e.preventDefault();
		const formData = new FormData(this);

		const openSpaceM2 = parseFloat(formData.get("openSpace")) || 0;
		const openSpaceSqFt = +(openSpaceM2 * 10.7639).toFixed(2); // convert to sq ft

		const payload = {
			state: formData.get("state") || "",
			city: formData.get("city") || "",
			roof: formData.get("roof") || "",
			area: openSpaceSqFt,
			population: parseInt(formData.get("dwellers")) || 0,
			budget: formData.get("budget")
				? parseFloat(formData.get("budget"))
				: null,
		};

		console.log("Form Payload:", payload);
		spinner.style.display = "flex";
		try {
			const response = await fetch(
				"https://aquabytes.onrender.com/api/v1/rtwh/feasibility",
				{
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify(payload),
				},
			);

			if (!response.ok) throw new Error("Network response was not ok");

			const result = await response.json();
			localStorage.setItem("rainwaterResult", JSON.stringify(result));
			window.location.href = "result.html";
		} catch (err) {
			console.error("Failed to fetch feasibility:", err);
			alert("Error fetching feasibility. Check console.");
		}
		window.location.href = "./output";
		spinner.style.display = "none";
	});
});
