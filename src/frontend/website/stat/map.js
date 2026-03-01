const map = L.map("map").setView([22, 79], 4);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

// Complete dummy dataset
const stateData = {
	"Andhra Pradesh": { rainfall: 900, groundwater: 45 },
	"Arunachal Pradesh": { rainfall: 2200, groundwater: 60 },
	Assam: { rainfall: 1800, groundwater: 55 },
	Bihar: { rainfall: 800, groundwater: 25 },
	Chhattisgarh: { rainfall: 1200, groundwater: 40 },
	Goa: { rainfall: 3000, groundwater: 50 },
	Gujarat: { rainfall: 600, groundwater: 30 },
	Haryana: { rainfall: 550, groundwater: 28 },
	"Himachal Pradesh": { rainfall: 1250, groundwater: 35 },
	Jharkhand: { rainfall: 1400, groundwater: 42 },
	Karnataka: { rainfall: 900, groundwater: 55 },
	Kerala: { rainfall: 3200, groundwater: 60 },
	"Madhya Pradesh": { rainfall: 850, groundwater: 38 },
	Maharashtra: { rainfall: 1200, groundwater: 40 },
	Manipur: { rainfall: 1800, groundwater: 50 },
	Meghalaya: { rainfall: 3500, groundwater: 65 },
	Mizoram: { rainfall: 2500, groundwater: 55 },
	Nagaland: { rainfall: 1800, groundwater: 50 },
	Odisha: { rainfall: 1500, groundwater: 45 },
	Punjab: { rainfall: 500, groundwater: 28 },
	Rajasthan: { rainfall: 400, groundwater: 20 },
	Sikkim: { rainfall: 2800, groundwater: 55 },
	"Tamil Nadu": { rainfall: 1000, groundwater: 50 },
	Telangana: { rainfall: 900, groundwater: 40 },
	Tripura: { rainfall: 1700, groundwater: 50 },
	"Uttar Pradesh": { rainfall: 700, groundwater: 35 },
	Uttarakhand: { rainfall: 1300, groundwater: 42 },
	"West Bengal": { rainfall: 1400, groundwater: 45 },
	"Andaman and Nicobar Islands": { rainfall: 3000, groundwater: 55 },
	Chandigarh: { rainfall: 800, groundwater: 25 },
	"Dadra and Nagar Haveli and Daman and Diu": {
		rainfall: 1200,
		groundwater: 35,
	},
	Delhi: { rainfall: 600, groundwater: 30 },
	"Jammu and Kashmir": { rainfall: 1000, groundwater: 40 },
	Ladakh: { rainfall: 50, groundwater: 5 },
	Lakshadweep: { rainfall: 2500, groundwater: 50 },
	Puducherry: { rainfall: 1200, groundwater: 45 },
};

let currentType = "rainfall";

function getColor(value, type) {
	if (type === "rainfall") {
		// Blue scale for rainfall
		return value > 1200
			? "#08306b"
			: value > 1000
			? "#2171b5"
			: value > 800
			? "#4292c6"
			: value > 600
			? "#6baed6"
			: value > 400
			? "#9ecae1"
			: "#c6dbef";
	} else {
		// Green scale for groundwater
		return value > 60
			? "#00441b"
			: value > 50
			? "#006d2c"
			: value > 40
			? "#238b45"
			: value > 30
			? "#41ae76"
			: value > 20
			? "#66c2a4"
			: "#c7e9c0";
	}
}

function styleFeature(feature, type) {
	const name = feature.properties.st_nm;
	const value = stateData[name] ? stateData[name][type] : 0;
	return {
		fillColor: getColor(value, type),
		weight: 1,
		color: "white",
		fillOpacity: 0.7,
	};
}

function onEachFeature(feature, layer) {
	const name = feature.properties.st_nm;
	const data = stateData[name];
	layer.bindPopup(`
    <strong>${name}</strong><br>
    Rainfall: ${data ? data.rainfall : 0} mm<br>
    Groundwater: ${data ? data.groundwater : 0} m
  `);
}

const geoJsonUrl =
	"https://cdn.jsdelivr.net/gh/udit-001/india-maps-data@bcbcba3/geojson/india.geojson";
let geoLayer;

function loadMap() {
	fetch(geoJsonUrl)
		.then((res) => res.json())
		.then((data) => {
			geoLayer = L.geoJSON(data, {
				style: (f) => styleFeature(f, currentType),
				onEachFeature: onEachFeature,
			}).addTo(map);
		});
}

loadMap();

// Toggle button
document.getElementById("toggleButton").addEventListener("click", () => {
	currentType = currentType === "rainfall" ? "groundwater" : "rainfall";
	if (geoLayer) map.removeLayer(geoLayer);
	loadMap();
	document.getElementById("toggleButton").textContent =
		currentType === "rainfall" ? "Show Groundwater" : "Show Rainfall";
	updateLegend();
});

// Legend
const legend = L.control({ position: "bottomright" });
legend.onAdd = function () {
	const div = L.DomUtil.create("div", "legend");
	const grades =
		currentType === "rainfall"
			? [500, 1000, 1500, 2000, 3000]
			: [20, 30, 40, 50, 60];
	div.innerHTML = `<strong>${
		currentType === "rainfall" ? "Rainfall (mm)" : "Groundwater (m)"
	}</strong><br>`;
	grades.forEach((g) => {
		div.innerHTML += `<i style="background:${getColor(
			g,
			currentType
		)}"></i> ${g}+<br>`;
	});
	return div;
};
legend.addTo(map);

function updateLegend() {
	legend.remove();
	legend.addTo(map);
}
