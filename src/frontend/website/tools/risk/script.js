// Utilities
const $ = (id) => document.getElementById(id);
const spinner = $("spinnerOverlay");
const stateSelect = $("state");
const citySelect = $("city");
const stateLiveSelect = $("state_live");
const cityLiveSelect = $("city_live");

// Choices.js instances
let stateChoices, cityChoices, stateLiveChoices, cityLiveChoices;
let chart = null;

function formatNumber(n) {
	return n == null || isNaN(n)
		? "-"
		: (Math.round(n * 100) / 100).toLocaleString();
}

function refreshLocalCalc() {
	const current = Number($("current_level").value) || 0;
	const population = Number($("population").value) || 0;
	const avg_need = 135;
	const dailyUse = population * avg_need;
	const days = dailyUse > 0 ? current / dailyUse : null;

	if (days === null) {
		$("bigDisplay").innerText = "— days left";
	} else {
		const d = Math.floor(days);
		const h = Math.floor((days - d) * 24);
		$("bigDisplay").innerText = `${formatNumber(days)} days (${d}d ${h}h)`;
	}
}

function createChart(values) {
	const ctx = $("rainChart").getContext("2d");
	const labels = values.map((_, i) => `Day ${i + 1}`);

	if (chart) chart.destroy();

	chart = new Chart(ctx, {
		type: "bar",
		data: {
			labels,
			datasets: [
				{
					label: "Rain (mm)",
					data: values,
					backgroundColor: "#3b82f6",
					borderRadius: 6,
				},
			],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			scales: { y: { beginAtZero: true } },
			plugins: { legend: { display: false } },
		},
	});
}

function populateStates() {
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

	states.forEach((s) => {
		stateChoices.setChoices([{ value: s, label: s }], "value", "label", false);
		stateLiveChoices.setChoices(
			[{ value: s, label: s }],
			"value",
			"label",
			false,
		);
	});
}

async function fetchCities(state) {
	try {
		spinner.style.display = "flex";

		const cached = localStorage.getItem(`cities_${state}`);
		if (cached) {
			spinner.style.display = "none";
			return JSON.parse(cached);
		}

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
		return data.data;
	} catch (err) {
		console.error(err);
		spinner.style.display = "none";
		alert(`Failed to load cities for ${state}`);
		return [];
	}
}

function populateReport(obj) {
	$("phVal").innerText = obj.ph ?? "-";
	$("tdsVal").innerText = obj.tds != null ? obj.tds + " ppm" : "-";

	const storage =
		obj.storage_risk === 0 ? "Low" : obj.storage_risk === 1 ? "High" : "-";
	const quality =
		obj.quality_risk === 0 ? "Low" : obj.quality_risk === 1 ? "High" : "-";

	$("storageRisk").innerText = storage;
	$("qualityRisk").innerText = quality;

	const getColor = (val) =>
		val === "Low" ? "#16a34a" : val === "High" ? "#dc2626" : "#6b7280";

	$("storageRisk").style.color = getColor(storage);
	$("qualityRisk").style.color = getColor(quality);

	$("overallSuggestion").innerText = obj.overall_suggestion ?? "-";

	const tipsList = $("tipsList");
	tipsList.innerHTML = "";
	(obj.storage_tips || []).forEach((t) => {
		const li = document.createElement("li");
		li.innerText = t;
		tipsList.appendChild(li);
	});

	createChart(obj.rain_forecast || [0, 0, 0, 0, 0]);
}

// -------- Submit Form -------- //
async function handleSubmit(e) {
	e.preventDefault();

	const state = stateSelect.value;
	const city = citySelect.value;
	const tank_cap = Number($("tank_cap").value) || 0;
	const current_level = Number($("current_level").value) || 0;
	const population = Number($("population").value) || 0;
	const avg_need = 135;

	if (!state || !city || population <= 0) {
		$("formMsg").innerText = "Please fill all required fields!";
		return;
	}

	$("formMsg").innerText = "";
	spinner.style.display = "flex";

	try {
		refreshLocalCalc();

		const payload = {
			state,
			city,
			tank_cap,
			current_level,
			population,
			avg_need,
		};

		if (sensor) {
			payload.ph = sensor.ph;
			payload.tds = sensor.tds;
		}

		const response = await fetch(
			"https://aquabytes.onrender.com/api/v1/water-risk/ESP32_001",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Accept: "application/json",
				},
				body: JSON.stringify(payload),
			},
		);

		const data = await response.json();
		populateReport(data);
		$("formMsg").innerText = "Report generated!";
	} catch (err) {
		console.error(err);
		$("formMsg").innerText = "Failed to fetch report.";
	} finally {
		spinner.style.display = "none";
	}
}

function handleReset() {
	$("waterForm").reset();
	refreshLocalCalc();
	populateReport({});
	$("formMsg").innerText = "";
}

// DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
	stateChoices = new Choices("#state", {
		searchEnabled: true,
		shouldSort: false,
	});
	cityChoices = new Choices("#city", {
		searchEnabled: true,
		shouldSort: false,
	});
	stateLiveChoices = new Choices("#state_live", {
		searchEnabled: true,
		shouldSort: false,
	});
	cityLiveChoices = new Choices("#city_live", {
		searchEnabled: true,
		shouldSort: false,
	});

	populateStates();
	createChart([0, 0, 0, 0, 0]);
	refreshLocalCalc();

	stateSelect.addEventListener("change", async function () {
		const state = this.value;
		const cities = await fetchCities(state);
		cityChoices.clearStore();
		cities.forEach((c) =>
			cityChoices.setChoices([{ value: c, label: c }], "value", "label", false),
		);
	});

	stateLiveSelect.addEventListener("change", async function () {
		const state = this.value;
		const cities = await fetchCities(state);
		cityLiveChoices.clearStore();
		cities.forEach((c) =>
			cityLiveChoices.setChoices(
				[{ value: c, label: c }],
				"value",
				"label",
				false,
			),
		);
	});

	$("waterForm").addEventListener("submit", handleSubmit);
	$("resetBtn").addEventListener("click", handleReset);
});
