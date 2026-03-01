import React from "react";
import { View, Text, StyleSheet, Dimensions } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { useTranslation } from "react-i18next";

const { width } = Dimensions.get("window");

const FeasibilityScoreCard = ({ score }) => {
	const { t } = useTranslation();

	const getLabelAndColors = (s) => {
		if (s >= 80)
			return {
				label: t("feasibility.labels.excellent"),
				colors: ["#22c55e", "#15803d"],
			};
		if (s >= 60)
			return {
				label: t("feasibility.labels.great"),
				colors: ["#3b82f6", "#1e3a8a"],
			};
		if (s >= 40)
			return {
				label: t("feasibility.labels.average"),
				colors: ["#facc15", "#ca8a04"],
			};
		if (s >= 20)
			return {
				label: t("feasibility.labels.poor"),
				colors: ["#f97316", "#c2410c"],
			};
		return {
			label: t("feasibility.labels.veryPoor"),
			colors: ["#ef4444", "#991b1b"],
		};
	};

	const roundedScore = Math.round(score);
	const { label, colors } = getLabelAndColors(roundedScore);

	return (
		<LinearGradient colors={colors} style={styles.container}>
			<Text style={styles.title}>{t("feasibility.title")}</Text>

			<View style={styles.circle}>
				<Text style={styles.score}>{roundedScore}</Text>
				<Text style={styles.of}>{t("feasibility.of")}</Text>
			</View>

			<Text style={styles.label}>{label}</Text>
		</LinearGradient>
	);
};

const styles = StyleSheet.create({
	container: {
		width: width - 40,
		alignSelf: "center",
		borderRadius: 16,
		paddingVertical: 40,
		paddingHorizontal: 20,
		alignItems: "center",
		justifyContent: "center",
		marginVertical: 20,
	},
	title: {
		color: "#fff",
		fontSize: 16,
		fontWeight: "bold",
		marginBottom: 20,
	},
	circle: {
		width: 150,
		height: 150,
		borderRadius: 75,
		backgroundColor: "rgba(255,255,255,0.15)",
		alignItems: "center",
		justifyContent: "center",
		marginBottom: 20,
	},
	score: {
		fontSize: 42,
		fontWeight: "bold",
		color: "#fff",
	},
	of: {
		fontSize: 16,
		color: "#fff",
	},
	label: {
		fontSize: 20,
		fontWeight: "bold",
		color: "#fff",
	},
});

export default FeasibilityScoreCard;
