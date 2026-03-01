// OutputPage.jsx
import React from "react";
import {
	View,
	ScrollView,
	Text,
	StyleSheet,
	TouchableOpacity,
} from "react-native";
import FeasibilityScore from "./FeasibilityScore";
import SummaryCard from "./sum_card";
import { router } from "expo-router";

export default function OutputPage({ response }) {
	const parsedResponse = response || {};
	const score = parsedResponse?.score ?? 0;

	return (
		<View style={styles.container}>
			<ScrollView contentContainerStyle={styles.scrollContainer}>
				{/* Feasibility Score */}
				<FeasibilityScore score={score} />

				{/* Detailed Info */}
				<SummaryCard response={response} />

				{/* Buttons */}
				<TouchableOpacity
					style={[styles.button, styles.consultButton]}
					onPress={() => router.push("/chatbot")}>
					<Text style={styles.buttonText}>CONSULT</Text>
				</TouchableOpacity>

				<TouchableOpacity
					style={[styles.button, styles.backButton]}
					onPress={() => router.back()}>
					<Text style={styles.buttonText}>GO BACK</Text>
				</TouchableOpacity>
			</ScrollView>
		</View>
	);
}

const styles = StyleSheet.create({
	container: { flex: 1, backgroundColor: "#fefefe" },
	scrollContainer: {
		padding: 20,
		alignItems: "center",
		width: "100%",
	},
	button: {
		width: "95%", // almost full width
		paddingVertical: 16,
		borderRadius: 12,
		marginVertical: 10,
		alignItems: "center",
		shadowColor: "#000",
		shadowOpacity: 0.15,
		shadowRadius: 6,
		shadowOffset: { width: 0, height: 3 },
		elevation: 5, // for Android shadow
	},
	consultButton: {
		backgroundColor: "#28f6bb",
	},
	backButton: {
		backgroundColor: "#2563eb",
	},
	buttonText: {
		color: "#fff",
		fontSize: 16,
		fontWeight: "bold",
	},
});
