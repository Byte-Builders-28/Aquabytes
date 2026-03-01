document.addEventListener("DOMContentLoaded", () => {
	const spinner = document.getElementById("spinnerOverlay");

	const deviceModalEl = document.getElementById("deviceModal");
	const deviceModal = new bootstrap.Modal(deviceModalEl, {
		backdrop: "static",
		keyboard: false,
	});

	let currentDeviceId = null;

	deviceModal.show();

	async function fetchData(deviceId) {
		currentDeviceId = deviceId;
		spinner.style.display = "flex";

		try {
			const res = await fetch(
				`https://aquabytes.onrender.com/api/v1/devices/${device_id}/water-quality/predict`,
				{
					method: "POST",
					headers: { accept: "application/json" },
					body: "",
				},
			);
			const data = await res.json();
			populateData(data);
		} catch (err) {
			alert("Error fetching data: " + err.message);
		} finally {
			spinner.style.display = "none";
		}
	}

	// Device form submit
	const deviceForm = document.getElementById("deviceForm");
	deviceForm.addEventListener("submit", (e) => {
		e.preventDefault();
		const deviceId = document.getElementById("deviceId").value.trim();
		if (!deviceId) return;

		deviceModal.hide();
		fetchData(deviceId);
	});

	// Change device button
	document.getElementById("changeDeviceBtn").addEventListener("click", () => {
		deviceModal.show();
	});

	// Recalculate button
	document.getElementById("recalcBtn").addEventListener("click", () => {
		if (!currentDeviceId) {
			deviceModal.show();
			return;
		}
		fetchData(currentDeviceId);
	});

	function populateData(data) {
		const sensor = data.data.sensor_data;
		const wqi = data.data.wqi;

		document.getElementById("wqiVal").textContent = wqi.wqi;
		document.getElementById("wqiCategory").textContent = wqi.category;
		document.getElementById("wqiDevice").textContent =
			`${sensor.device_id} · ${sensor.location}`;

		// Parameters
		const params = ["ph", "tds", "turbidity", "do", "temperature"];
		const paramList = document.getElementById("paramList");
		paramList.innerHTML = "";

		params.forEach((p) => {
			const div = document.createElement("div");
			div.className = `col-md-3 param ${
				wqi.sub_indices[p] >= 80
					? "safe"
					: wqi.sub_indices[p] >= 50
						? "warn"
						: "danger"
			}`;

			div.innerHTML = `
				<div class="param-label">${p.toUpperCase()}</div>
				<div class="param-value">
					${sensor[p]}
					${
						p === "tds"
							? " ppm"
							: p === "turbidity"
								? " NTU"
								: p === "temperature"
									? " °C"
									: " mg/L"
					}
				</div>
			`;
			paramList.appendChild(div);
		});

		// Risks
		document.getElementById("microbialRisk").textContent =
			data.data.microbial_risk.level;
		document.getElementById("heavyMetalRisk").textContent =
			data.data.heavy_metal_risk.level;

		// Usage
		const usageList = document.getElementById("usageList");
		usageList.innerHTML = "";

		const usage = data.data.rooftop_harvest.suitable_purposes;
		let usageEmpty = true;

		for (const [k, v] of Object.entries(usage)) {
			const li = document.createElement("li");
			const span = document.createElement("strong");
			span.textContent = v ? "Allowed" : "Not suitable";
			span.className = v ? "text-success" : "text-danger";

			li.textContent = k.charAt(0).toUpperCase() + k.slice(1) + ": ";
			li.appendChild(span);
			usageList.appendChild(li);
			usageEmpty = false;
		}

		if (usageEmpty) usageList.textContent = "Nothing to see here.";

		// Alerts
		const alertContainer = document.getElementById("alertContainer");
		const alertBadge = document.getElementById("alertBadge");

		alertContainer.innerHTML = "";

		if (!data.data.alerts || data.data.alerts.length === 0) {
			alertContainer.textContent = "Nothing to see here.";
			alertBadge.style.display = "none";
		} else {
			data.data.alerts.forEach((a) => {
				const div = document.createElement("div");
				div.className = `alert ${
					a.severity === "high" || a.severity === "critical"
						? "alert-danger"
						: "alert-warning"
				}`;
				div.textContent = a.message;
				alertContainer.appendChild(div);
			});
			alertBadge.innerText = data.data.alerts.length;
			alertBadge.style.display = "inline-block";
		}

		// Recommendations
		const recContainer = document.getElementById("recContainer");
		const recBadge = document.getElementById("recBadge");

		recContainer.innerHTML = "";

		if (!data.data.recommendations || data.data.recommendations.length === 0) {
			recContainer.textContent = "Nothing to see here.";
			recBadge.style.display = "none";
		} else {
			const ul = document.createElement("ul");
			data.data.recommendations.forEach((r) => {
				const li = document.createElement("li");
				li.textContent = r;
				ul.appendChild(li);
			});
			recContainer.appendChild(ul);
			recBadge.innerText = data.data.recommendations.length;
			recBadge.style.display = "inline-block";
		}
	}
});
