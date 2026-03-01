// --- Setup map (✅ cap maxZoom to 18) ---
const map = L.map("map", {
	zoomControl: true,
	maxZoom: 18,
}).setView([20, 78], 5);

// Base layers
const street = L.tileLayer(
	"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
	{
		attribution: "© OpenStreetMap contributors",
		maxZoom: 18,
	},
);

const satellite = L.tileLayer(
	"https://server.arcgisonline.com/ArcGIS/rest/services/" +
		"World_Imagery/MapServer/tile/{z}/{y}/{x}",
	{
		attribution: "Tiles © Esri &mdash; Source: Esri, Maxar",
		maxZoom: 18,
	},
).addTo(map);

// Layer switcher
L.control.layers({ Street: street, Satellite: satellite }).addTo(map);

// UI elements
const statusEl = document.getElementById("status");
const locateBtn = document.getElementById("locateBtn");
const finishBtn = document.getElementById("finishBtn");
const clearBtn = document.getElementById("clearBtn");
const openSpaceInput = document.getElementById("openSpace");
const mapContainer = document.getElementById("mapContainer");
const useMapBtn = document.getElementById("useMapBtn");
const stateSelect = document.getElementById("state");
const citySelect = document.getElementById("city");

// backend link

const base_url = "https://aquabytes.onrender.com";

// Polygon state
let points = [];
let markers = [];
let previewLine = null;
let polygon = null;
let userLocationMarker = null;

function setStatus(text) {
	statusEl.textContent = text;
}

// --- Reverse geocode using Nominatim ---
async function reverseGeocode(lat, lng) {
	try {
		const res = await fetch(`${base_url}/api/v1/geocode?lat=${lat}&lng=${lng}`);
		const data = await res.json();
		return {
			state: data.state || "",
			city: data.city || "",
		};
	} catch (err) {
		console.error("Reverse geocode failed:", err);
		return { state: "", city: "" };
	}
}

// --- Locate user ---
async function locateUser(animate = true, autofill = true) {
	if (!navigator.geolocation) {
		setStatus("Geolocation not supported by your browser.");
		return;
	}
	setStatus("Locating…");
	navigator.geolocation.getCurrentPosition(
		async (pos) => {
			const lat = pos.coords.latitude;
			const lng = pos.coords.longitude;
			setStatus(`Located: ${lat.toFixed(5)}, ${lng.toFixed(5)}`);
			if (userLocationMarker) userLocationMarker.remove();
			userLocationMarker = L.circleMarker([lat, lng], {
				radius: 7,
				weight: 1,
				fillOpacity: 0.9,
				color: "red",
			})
				.addTo(map)
				.bindPopup("You are here")
				.openPopup();
			if (animate) map.setView([lat, lng], 16, { animate: true });

			if (autofill) {
				const loc = await reverseGeocode(lat, lng);
				if (loc.state) stateSelect.value = loc.state;
				stateSelect.dispatchEvent(new Event("change"));
				if (loc.city) {
					const startTime = Date.now();
					const interval = setInterval(() => {
						if (citySelect.options.length > 0) {
							citySelect.value = loc.city;
							clearInterval(interval); // stop polling
						} else if (Date.now() - startTime > 5000) {
							// 5 seconds max
							clearInterval(interval);
							console.warn("City options never loaded.");
						}
					}, 100); // check every 100ms
				}
			}
		},
		(err) => setStatus("Could not get location: " + (err.message || err.code)),
		{ enableHighAccuracy: true, timeout: 10000, maximumAge: 0 },
	);
}
locateUser(false, true);

// --- Update area live ---
function updateArea() {
	if (points.length < 3) {
		openSpaceInput.value = "";
		return;
	}
	const coords = points.map((p) => [p.lng, p.lat]);
	coords.push([points[0].lng, points[0].lat]);
	const polygonGeoJSON = turf.polygon([coords]);
	const area = turf.area(polygonGeoJSON); // m²
	openSpaceInput.value = area.toFixed(2);
}

// --- Map click to add points ---
map.on("click", function (e) {
	if (polygon) {
		setStatus("Polygon finished — click Clear to draw another.");
		return;
	}
	const latlng = e.latlng;
	points.push(latlng);
	const m = L.circleMarker(latlng, { radius: 5 }).addTo(map);
	markers.push(m);

	if (previewLine) map.removeLayer(previewLine);
	previewLine = L.polyline(points, { dashArray: "6 6" }).addTo(map);

	updateArea();
	setStatus(`${points.length} point(s). Click Finish polygon when ready.`);
});

// --- Finish polygon ---
finishBtn.addEventListener("click", () => {
	if (points.length < 3) {
		setStatus("Need at least 3 points to make a polygon.");
		return;
	}
	if (previewLine) {
		map.removeLayer(previewLine);
		previewLine = null;
	}
	polygon = L.polygon(points, {
		color: "#3388ff",
		weight: 2,
		fillOpacity: 0.25,
	}).addTo(map);
	setStatus(
		`Polygon created with ${points.length} points. Use Clear to draw again.`,
	);
	map.fitBounds(polygon.getBounds().pad(0.18));

	updateArea();
});

// --- Clear polygon ---
clearBtn.addEventListener("click", () => {
	points = [];
	markers.forEach((m) => map.removeLayer(m));
	markers = [];
	if (previewLine) {
		map.removeLayer(previewLine);
		previewLine = null;
	}
	if (polygon) {
		map.removeLayer(polygon);
		polygon = null;
	}
	openSpaceInput.value = "";
	setStatus("Cleared. Click on the map to add polygon vertices.");
});

// --- Toggle map display ---
useMapBtn.addEventListener("click", () => {
	mapContainer.style.display =
		mapContainer.style.display === "none" ? "block" : "none";
	setTimeout(() => map.invalidateSize(), 300);
});

// --- Recenter user ---
locateBtn.addEventListener("click", () => locateUser(true, true));

// --- Zoom to city when selection changes ---
citySelect.addEventListener("change", async () => {
	const city = citySelect.value;
	const state = stateSelect.value;
	if (!city) return;

	const address = state ? `${city}, ${state}` : city;

	try {
		const res = await fetch(
			`${base_url}/api/v1/geocode?address=${encodeURIComponent(address)}`,
		);
		const data = await res.json();
		if (data.latitude && data.longitude) {
			map.setView([data.latitude, data.longitude], 14, { animate: true });
		} else {
			console.warn("No coordinates returned for", address);
		}
	} catch (err) {
		console.error("Failed to geocode city:", err);
	}
});
