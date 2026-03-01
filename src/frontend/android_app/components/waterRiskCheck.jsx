// components/WaterRiskCheck.jsx
import React, { useState } from "react";
import {
	View,
	Text,
	TextInput,
	Button,
	StyleSheet,
	ScrollView,
	Alert,
	Dimensions,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";

import { readSavedLink } from "../utils/helpers";

const screenWidth = Dimensions.get("window").width;

export default function WaterRiskCheck() {
	const { t } = useTranslation();
	const router = useRouter();

	const [capacity, setCapacity] = useState("");
	const [current, setCurrent] = useState("");
	const [loading, setLoading] = useState(false);

	const promptMissingData = () => {
		Alert.alert(
			t("waterRiskCheck.surveyRequired"),
			t("waterRiskCheck.surveyMessage"),
			[{ text: "OK" }],
		);
	};

	const handleSubmit = async () => {
		if (!capacity || !current) {
			Alert.alert(
				t("waterRiskCheck.inputMissing"),
				t("waterRiskCheck.inputMissingMsg"),
			);
			return;
		}

		// Read cache from AsyncStorage at button press
		let latestCache = null;
		try {
			const storedHistory = await AsyncStorage.getItem("surveyHistory");
			if (storedHistory) {
				const historyArr = JSON.parse(storedHistory);
				if (Array.isArray(historyArr) && historyArr.length > 0) {
					const latest = historyArr[historyArr.length - 1]; // last item
					if (latest.payload) {
						latestCache = {
							state: latest.payload.state || "",
							city: latest.payload.city || "",
							population: parseInt(latest.payload.population, 10) || 0,
						};
					}
				}
			}
		} catch (err) {
			console.error("❌ Error reading cache:", err);
		}

		if (!latestCache) {
			promptMissingData();
			return;
		}

		const tankCap = parseInt(capacity.trim(), 10);
		const currLevel = parseInt(current.trim(), 10);

		if (isNaN(tankCap) || isNaN(currLevel)) {
			Alert.alert("Invalid Input", "Please enter valid numbers.");
			return;
		}

		if (currLevel > tankCap) {
			Alert.alert(
				"Invalid Input",
				"Water level cannot be higher than tank capacity.",
			);
			return;
		}

		setLoading(true);

		try {
			const payload = {
				state: latestCache.state,
				city: latestCache.city,
				tank_cap: tankCap,
				current_level: currLevel,
				population: latestCache.population,
				avg_need: 135,
			};

			const linkdata = await readSavedLink();
			const base_link = linkdata.currentLink;
			const url = base_link.endsWith("/")
				? `${base_link}api/v1/water-risk/ESP32_001`
				: `${base_link}/api/v1/water-risk/ESP32_001`;

			const response = await fetch(url, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(payload),
			});

			const data = await response.json();

			router.push({
				pathname: "/waterHub",
				params: { result: JSON.stringify(data) },
			});
		} catch (err) {
			console.error(err);
			Alert.alert("Error", "Failed to fetch water risk from server.");
		} finally {
			setLoading(false);
		}
	};

	return (
		<ScrollView contentContainerStyle={styles.container}>
			<View style={styles.card}>
				<Text style={styles.cardTitle}>{t("waterRiskCheck.header")}</Text>

				<TextInput
					style={styles.input}
					placeholder={t("waterRiskCheck.tankCapacity")}
					placeholderTextColor="#ccc"
					keyboardType="numeric"
					value={capacity}
					onChangeText={setCapacity}
				/>
				<TextInput
					style={styles.input}
					placeholder={t("waterRiskCheck.currentWaterLevel")}
					placeholderTextColor="#ccc"
					keyboardType="numeric"
					value={current}
					onChangeText={setCurrent}
				/>

				<Button
					title={
						loading
							? t("waterRiskCheck.checking")
							: t("waterRiskCheck.checkRisk")
					}
					onPress={handleSubmit}
					disabled={loading}
				/>
			</View>
		</ScrollView>
	);
}

const styles = StyleSheet.create({
	container: {
		padding: 20,
		alignItems: "center",
		backgroundColor: "#f1f1f1ff",
	},
	card: {
		marginTop: 20,
		padding: 20,
		borderRadius: 16,
		backgroundColor: "#bedee8",
		shadowColor: "#000",
		shadowOpacity: 0.1,
		shadowRadius: 8,
		shadowOffset: { width: 0, height: 4 },
		elevation: 5,
		width: "100%",
	},
	cardTitle: {
		fontSize: 18,
		fontWeight: "700",
		marginBottom: 12,
		color: "#1a1a1aff",
	},
	input: {
		borderWidth: 1,
		borderColor: "#ccc",
		borderRadius: 10,
		padding: 10,
		width: "100%",
		marginBottom: 15,
		backgroundColor: "#ffffffff",
		color: "#1a1a1ffa",
	},
});
