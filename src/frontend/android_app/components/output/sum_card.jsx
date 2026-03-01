import { router } from "expo-router";
import React from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { useTranslation } from "react-i18next";

export default function SummaryCard({ response }) {
	const { t } = useTranslation();

	if (!response) return null;

	return (
		<View style={styles.container}>
			<Text style={styles.header}>{t("summaryCard.header")}</Text>

			{/* COST */}
			<View style={[styles.card, { backgroundColor: "#fee2e2" }]}>
				<Text style={[styles.key, { color: "#dc2626" }]}>
					{t("summaryCard.cost")}
				</Text>
				<Text style={styles.value}>
					{t("summaryCard.units.currency")}{" "}
					{response.cost_estimate?.toLocaleString()}
				</Text>
			</View>

			{/* Groundwater */}
			<View style={[styles.card, { backgroundColor: "#fef3c7" }]}>
				<Text style={[styles.key, { color: "#d97706" }]}>
					{t("summaryCard.groundwater")}
				</Text>
				<Text style={styles.value}>
					{Math.round(response.gw_recharge)} {t("summaryCard.units.meter")}
				</Text>
			</View>

			{/* Type of System */}
			<View style={[styles.card, { backgroundColor: "#d1fae5" }]}>
				<Text style={[styles.key, { color: "#059669" }]}>
					{t("summaryCard.systemType")}
				</Text>
				<Text style={styles.value}>{response.system_type}</Text>
			</View>

			{/* Tank Size */}
			<View style={[styles.card, { backgroundColor: "#e0e7ff" }]}>
				<Text style={[styles.key, { color: "#4f46e5" }]}>
					{t("summaryCard.tankSize")}
				</Text>
				<Text style={styles.value}>
					{Math.round(response.tank_size)} {t("summaryCard.units.squareMeter")}
				</Text>
			</View>

			{/* Reason */}
			<View style={[styles.card, { backgroundColor: "#f3f4f6" }]}>
				<Text style={[styles.key, { color: "#111827" }]}>
					{t("summaryCard.reason")}:
				</Text>
				<Text style={[styles.value, { flex: 1, textAlign: "left" }]}>
					{response.reason}
				</Text>
			</View>

			{/* More Info */}
			<TouchableOpacity
				style={{ marginTop: 12 }}
				onPress={() =>
					router.push({
						pathname: "/output_info",
						params: { response: JSON.stringify(response) },
					})
				}>
				<Text style={styles.moreInfo}>{t("summaryCard.moreInfo")}</Text>
			</TouchableOpacity>
		</View>
	);
}

const styles = StyleSheet.create({
	container: {
		width: "100%",
		padding: 16,
		backgroundColor: "#fff",
		borderRadius: 12,
		marginTop: 20,
		shadowColor: "#000",
		shadowOpacity: 0.05,
		shadowRadius: 4,
		elevation: 2,
	},
	header: {
		fontWeight: "bold",
		fontSize: 16,
		marginBottom: 12,
		color: "#111",
	},
	card: {
		flexDirection: "row",
		justifyContent: "space-between",
		padding: 12,
		borderRadius: 8,
		marginBottom: 10,
	},
	key: {
		fontWeight: "600",
		fontSize: 14,
	},
	value: {
		fontSize: 14,
		fontWeight: "500",
		color: "#111827",
	},
	moreInfo: {
		fontSize: 13,
		fontWeight: "500",
		color: "#2563eb",
		textAlign: "right",
	},
});
