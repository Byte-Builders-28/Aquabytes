var ctx = document.getElementById("trendChart").getContext("2d");
new Chart(ctx, {
	type: "line",
	data: {
		labels: [
			2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011,
			2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023,
			2024, 2025,
		],
		datasets: [
			{
				label: "Rooftop RWH Adoption Index",
				data: [
					5, 6, 7, 8, 9, 10, 12, 15, 18, 22, 28, 33, 40, 45, 50, 55, 58, 61, 64,
					67, 70, 72, 74, 76, 78, 80,
				],
				borderColor: "#0d6efd",
				backgroundColor: "rgba(13,110,253,0.3)",
				fill: true,
				tension: 0.3,
			},
		],
	},
});

$(document).ready(function () {
	$("#projectTable").DataTable();
});
