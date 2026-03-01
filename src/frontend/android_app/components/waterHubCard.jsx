import React from "react";
import { View, Text, Dimensions, StyleSheet } from "react-native";
import { BarChart } from "react-native-chart-kit";

const screenWidth = Dimensions.get("window").width;

export default function HubResultCard({ result }) {
	if (!result) return null;

	const alertText =
		result.storage_risk === 1
			? "Less Groundwater. No Rain for 5 days"
			: "Water levels are safe";

	return (
		<View style={styles.card}>
			{/* Rainfall Bar Chart */}
			{result.rain_forecast && result.rain_forecast.length > 0 && (
				<>
					<Text style={[styles.cardSubtitle, { marginTop: 15 }]}>
						Last 5 Days Rainfall
					</Text>
					<BarChart
						data={{
							labels: ["D1", "D2", "D3", "D4", "D5"],
							datasets: [
								{
									data: result.rain_forecast,
								},
							],
						}}
						width={screenWidth - 85}
						height={200}
						withInnerLines={false}
						yAxisSuffix="mm"
						chartConfig={{
							backgroundGradientFrom: "rgba(39, 117, 206, 1)",
							backgroundGradientTo: "#2575fc",
							decimalPlaces: 0,
							color: () => `rgba(255, 255, 255, 1)`,
							labelColor: () => "#fff",
							style: { borderRadius: 16 },
						}}
						style={{ marginTop: 10, borderRadius: 16 }}
					/>

					{/* PH & TDS cards side by side */}
					<View style={styles.phTdsContainer}>
						<View style={styles.phTdsCard}>
							<Text style={styles.phTdsTitle}>pH</Text>
							<Text style={styles.phTdsValue}>{result.ph}</Text>
						</View>
						<View style={styles.phTdsCard}>
							<Text style={styles.phTdsTitle}>TDS</Text>
							<Text style={styles.phTdsValue}>{result.tds} ppm</Text>
						</View>
					</View>

					{/* Quality Risk card */}
					<View style={styles.qualityCard}>
						<Text style={styles.phTdsTitle}>Quality Risk</Text>
						<Text style={styles.phTdsValue}>
							{result.quality_risk === 1 ? "⚠️ High" : "✅ Low"}
						</Text>
						<Text style={styles.qualityMessage}>{result.quality_message}</Text>
					</View>
				</>
			)}

			{/* ALERT BANNER */}
			{result.storage_risk !== undefined && (
				<View
					style={[
						styles.alertBox,
						{
							backgroundColor:
								result.storage_risk === 1 ? "#ff4d4d" : "#4caf50",
						},
					]}>
					<Text style={styles.alertText}>
						{result.storage_risk === 1 ? "⚠️ " : "✅ "}
						{alertText}
					</Text>
				</View>
			)}

			{/* Suggestion */}
			<View style={styles.section}>
				<Text style={styles.sectionTitle}>Suggestion</Text>
				<View style={styles.suggestionBox}>
					<Text style={styles.suggestionText}>{result.overall_suggestion}</Text>
				</View>
			</View>

			{/* Tips */}
			<View style={styles.section}>
				<Text style={styles.sectionTitle}>Tips</Text>
				{result.storage_tips && result.storage_tips.length > 0 ? (
					result.storage_tips.map((tip, idx) => (
						<View key={idx} style={styles.tipBox}>
							<Text style={styles.tipText}>• {tip}</Text>
						</View>
					))
				) : (
					<Text style={styles.tipText}>No tips available</Text>
				)}
			</View>
		</View>
	);
}

const styles = StyleSheet.create({
	card: {
		margin: 20,
		padding: 20,
		borderRadius: 16,
		backgroundColor: "#daf2ef",
		shadowColor: "#000",
		shadowOpacity: 0.1,
		shadowRadius: 10,
		elevation: 3,
	},
	alertBox: {
		padding: 10,
		borderRadius: 8,
		marginVertical: 12,
	},
	alertText: {
		color: "#fff",
		fontWeight: "bold",
		textAlign: "center",
	},
	cardSubtitle: {
		fontSize: 16,
		fontWeight: "600",
		marginTop: 10,
	},
	section: {
		marginTop: 15,
	},
	sectionTitle: {
		fontSize: 16,
		fontWeight: "700",
		marginBottom: 8,
		color: "#333",
	},
	suggestionBox: {
		backgroundColor: "#e0f7fa",
		padding: 12,
		borderRadius: 12,
		shadowColor: "#000",
		shadowOpacity: 0.05,
		shadowRadius: 5,
		elevation: 2,
	},
	suggestionText: {
		fontSize: 14,
		color: "#00796b",
	},
	tipBox: {
		backgroundColor: "#fff3e0",
		padding: 10,
		borderRadius: 10,
		marginBottom: 6,
		shadowColor: "#000",
		shadowOpacity: 0.05,
		shadowRadius: 3,
		elevation: 1,
	},
	tipText: {
		fontSize: 14,
		color: "#f57c00",
	},
	phTdsContainer: {
		flexDirection: "row",
		justifyContent: "space-between",
		marginTop: 15,
	},
	phTdsCard: {
		flex: 1,
		marginHorizontal: 5,
		padding: 12,
		backgroundColor: "#fff",
		borderRadius: 12,
		alignItems: "center",
		shadowColor: "#000",
		shadowOpacity: 0.05,
		shadowRadius: 5,
		elevation: 2,
	},
	phTdsTitle: {
		fontSize: 14,
		fontWeight: "600",
		color: "#333",
		marginBottom: 6,
	},
	phTdsValue: {
		fontSize: 18,
		fontWeight: "700",
		color: "#000",
	},
	qualityCard: {
		marginTop: 12,
		padding: 12,
		backgroundColor: "#fff0f0",
		borderRadius: 12,
		alignItems: "center",
		shadowColor: "#000",
		shadowOpacity: 0.05,
		shadowRadius: 5,
		elevation: 2,
	},
	qualityMessage: {
		fontSize: 14,
		color: "#d32f2f",
		marginTop: 4,
		textAlign: "center",
	},
});
