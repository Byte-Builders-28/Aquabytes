import React from "react";
import { View, ScrollView, Text, StyleSheet, SafeAreaView } from "react-native";
import { useLocalSearchParams } from "expo-router";
import { route } from "expo-router";
import HubResultCard from "../components/waterHubCard";
import { useTranslation } from "react-i18next";

export default function HubResultPage() {
	const { t } = useTranslation();
	const { result } = useLocalSearchParams();

	let parsedResult = null;
	try {
		parsedResult = result ? JSON.parse(result) : null;
	} catch (e) {
		console.error("Failed to parse result:", e);
	}

	return (
		<SafeAreaView style={{ flex: 1 }}>
			<ScrollView contentContainerStyle={{ paddingVertical: 8 }}>
				<View style={styles.container}>
					{/* Page Header */}
					<Text style={styles.header}>{t("waterRiskCheck.header")}</Text>

					<HubResultCard result={parsedResult} />
				</View>
			</ScrollView>
		</SafeAreaView>
	);
}

const styles = StyleSheet.create({
	container: {
		paddingHorizontal: 8,
	},
	header: {
		fontSize: 22,
		fontWeight: "700",
		color: "#333",
		marginBottom: 20,
		textAlign: "center",
	},
});
