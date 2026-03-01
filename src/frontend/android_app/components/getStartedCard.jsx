import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Link } from "expo-router";
import { useTranslation } from "react-i18next";

import Spacer from "./spacer";

export default function StartCard() {
	const { t } = useTranslation();

	return (
		<View style={styles.card}>
			<Link href="/getinput" asChild>
				<TouchableOpacity style={styles.startButton}>
					<Text style={styles.startText}>{t("startCard.button")}</Text>
				</TouchableOpacity>
			</Link>

			<Spacer height={40} />

			<View style={styles.iconRow}>
				{/* Icon 1 */}
				<Link href="/404" asChild>
					<TouchableOpacity style={styles.iconBox}>
						<Ionicons name="stats-chart" size={24} color="#2563eb" />
						<Text style={styles.iconText}>{t("startCard.aroundYou")}</Text>
					</TouchableOpacity>
				</Link>

				{/* Icon 2 */}
				<Link href="/chatbot" asChild>
					<TouchableOpacity style={styles.iconBox}>
						<Ionicons name="book-outline" size={24} color="#2563eb" />
						<Text style={styles.iconText}>{t("startCard.consultant")}</Text>
					</TouchableOpacity>
				</Link>

				{/* Icon 3 */}
				<Link href="/404" asChild>
					<TouchableOpacity style={styles.iconBox}>
						<Ionicons name="people-outline" size={24} color="#2563eb" />
						<Text style={styles.iconText}>{t("startCard.contribution")}</Text>
					</TouchableOpacity>
				</Link>
			</View>
		</View>
	);
}

const styles = StyleSheet.create({
	card: {
		marginHorizontal: 20,
		marginTop: 30,
		backgroundColor: "#fff",
		borderRadius: 15,
		padding: 20,
		paddingBottom: 40,
		shadowColor: "#000",
		shadowOpacity: 0.1,
		shadowRadius: 10,
		elevation: 5,
	},
	startButton: {
		backgroundColor: "#2563eb",
		borderRadius: 10,
		paddingVertical: 12,
		marginVertical: 10,
	},
	startText: {
		color: "#fff",
		fontSize: 16,
		textAlign: "center",
		fontWeight: "bold",
	},
	iconRow: {
		flexDirection: "row",
		justifyContent: "space-around",
	},
	iconBox: {
		alignItems: "center",
	},
	iconText: {
		fontSize: 12,
		marginTop: 4,
	},
});
