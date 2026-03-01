// SurveyHistory.jsx
import React, { useEffect, useState } from "react";
import {
	View,
	Text,
	StyleSheet,
	FlatList,
	TouchableOpacity,
	SafeAreaView,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import OutputPage from "../components/output/output";

export default function History() {
	const [history, setHistory] = useState([]);
	const [selectedResponse, setSelectedResponse] = useState(null);

	// Load history from AsyncStorage
	const loadHistory = async () => {
		try {
			const storedHistory = await AsyncStorage.getItem("surveyHistory");
			if (storedHistory) setHistory(JSON.parse(storedHistory));
		} catch (error) {
			console.error("❌ Error loading history:", error);
		}
	};

	useEffect(() => {
		loadHistory();
	}, []);

	const formatDate = (ts) => {
		const d = new Date(ts);
		return d.toLocaleString();
	};

	if (selectedResponse) {
		// Show OutputPage for selected history
		return (
			<View style={{ flex: 1 }}>
				<OutputPage response={selectedResponse} />
			</View>
		);
	}

	return (
		<SafeAreaView style={{ flex: 1 }}>
			<View style={styles.container}>
				<Text style={styles.header}>History</Text>
				{history.length === 0 ? (
					<Text style={styles.emptyText}>No history found.</Text>
				) : (
					<FlatList
						data={history}
						keyExtractor={(_, index) => index.toString()}
						contentContainerStyle={{ paddingBottom: 20 }}
						renderItem={({ item }) => (
							<TouchableOpacity
								style={styles.card}
								onPress={() => setSelectedResponse(item.response)}>
								<Text style={styles.timestamp}>
									{formatDate(item.timestamp)}
								</Text>
								<Text style={styles.title}>Preview:</Text>
								{Object.entries(item.payload).map(([key, value]) => (
									<Text key={key} style={styles.text}>
										{key}: {value.toString()}
									</Text>
								))}
							</TouchableOpacity>
						)}
					/>
				)}
			</View>
		</SafeAreaView>
	);
}

const styles = StyleSheet.create({
	container: { flex: 1, padding: 16, backgroundColor: "#f5f5f5" },
	header: {
		fontSize: 24,
		fontWeight: "bold",
		marginBottom: 12,
		textAlign: "center",
	},
	card: {
		backgroundColor: "#fff",
		padding: 16,
		marginBottom: 12,
		borderRadius: 12,
		shadowColor: "#000",
		shadowOpacity: 0.1,
		shadowRadius: 6,
		shadowOffset: { width: 0, height: 3 },
		elevation: 4,
	},
	timestamp: { fontSize: 12, color: "#666", marginBottom: 6 },
	title: { fontWeight: "bold", marginBottom: 4 },
	text: { fontSize: 14, marginLeft: 6 },
	emptyText: {
		textAlign: "center",
		marginTop: 20,
		fontSize: 16,
		color: "#888",
	},
});
