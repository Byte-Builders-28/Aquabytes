import React from "react";
import {
	View,
	Text,
	StyleSheet,
	ScrollView,
	TouchableOpacity,
	Linking,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { readSavedLink } from "../utils/helpers";

export default function MoreInfo() {
	const { response } = useLocalSearchParams();
	const data = response ? JSON.parse(response) : {};

	const sections = [
		{
			icon: "💧",
			title: "Monthly Water Supply",
			value: `${Math.round(data.supply / 12)} L`,
		},
		{
			icon: "🏠",
			title: "Monthly Water Demand",
			value: `${Math.round(data.demand / 12)} L`,
		},
		{
			icon: "⚠️",
			title: "Monthly Unmet Demand",
			value: `${Math.round(data.unmet / 12)} L shortfall`,
		},
		{
			icon: "📊",
			title: "System Reliability",
			value: `${(data.reliability * 100).toFixed(1)}%`,
		},
		{
			icon: "💰",
			title: "Estimated Cost",
			value: `₹ ${Math.round(data.cost_estimate)}`,
		},
		{
			icon: "🌍",
			title: "Groundwater Recharge",
			value: `${Math.round(data.gw_recharge)} L`,
		},
		{
			icon: "🛢️",
			title: "Recommended Tank Size",
			value: `${Math.round(data.tank_size)} L`,
		},
		{ icon: "🛠️", title: "Recommended System", value: data.system_type },
	];

	// === open /webar/index.html on the saved base link ===
	const openBaseLink = async () => {
		try {
			const linkdata = await readSavedLink();
			const base_link = linkdata?.currentLink;
			if (base_link) {
				const url = base_link.endsWith("/")
					? `${base_link}webar/index.html`
					: `${base_link}/webar/index.html`;
				await Linking.openURL(url);
			} else {
				alert("No saved link found.");
			}
		} catch (err) {
			console.error("❌ Failed to open link:", err);
			alert("Failed to open link.");
		}
	};

	return (
		<View style={{ flex: 1 }}>
			<ScrollView
				style={styles.container}
				contentContainerStyle={{ paddingBottom: 100 }}>
				<Text style={styles.header}>Detailed Analysis</Text>

				{sections.map((item, idx) => (
					<View key={idx} style={styles.card}>
						<Text style={styles.icon}>{item.icon}</Text>
						<View style={{ flex: 1 }}>
							<Text style={styles.title}>{item.title}</Text>
							<Text style={styles.value}>{item.value}</Text>
						</View>
					</View>
				))}

				{/* Reason card */}
				<View style={[styles.card, { backgroundColor: "#f3f4f6" }]}>
					<Text style={styles.icon}>ℹ️</Text>
					<View style={{ flex: 1 }}>
						<Text style={styles.title}>Reason</Text>
						<Text style={styles.reason}>{data.reason}</Text>
					</View>
				</View>
			</ScrollView>

			{/* Floating FAB + Label combo */}
			<TouchableOpacity
				style={styles.fabContainer}
				activeOpacity={0.85}
				onPress={openBaseLink}>
				<View style={styles.labelContainer}>
					<Text style={styles.label}>Preview</Text>
				</View>
				<View style={styles.fab}>
					<Ionicons name="camera-outline" size={26} color="#fff" />
				</View>
			</TouchableOpacity>
		</View>
	);
}

const styles = StyleSheet.create({
	container: { flex: 1, backgroundColor: "#f9fafb", padding: 20 },
	header: {
		fontSize: 22,
		fontWeight: "bold",
		marginVertical: 20,
		color: "#111827",
	},
	card: {
		flexDirection: "row",
		alignItems: "center",
		backgroundColor: "#fff",
		padding: 16,
		borderRadius: 12,
		marginBottom: 14,
		shadowColor: "#000",
		shadowOpacity: 0.06,
		shadowRadius: 6,
		elevation: 3,
	},
	icon: { fontSize: 20, marginRight: 12 },
	title: { fontSize: 14, fontWeight: "600", color: "#374151" },
	value: { fontSize: 16, fontWeight: "500", color: "#111827", marginTop: 2 },
	reason: { fontSize: 14, color: "#374151", marginTop: 4, lineHeight: 20 },
	fabContainer: {
		position: "absolute",
		bottom: 48,
		right: 24,
		flexDirection: "row",
		alignItems: "center",
	},
	labelContainer: {
		backgroundColor: "#2563eb",
		paddingHorizontal: 16,
		height: 56,
		borderTopLeftRadius: 28,
		borderBottomLeftRadius: 28,
		justifyContent: "center",
		marginRight: -25,
	},
	label: {
		color: "#fff",
		fontSize: 15,
		fontWeight: "600",
		paddingHorizontal: 40,
	},
	fab: {
		backgroundColor: "#2563eb",
		width: 56,
		height: 56,
		borderRadius: 28,
		justifyContent: "center",
		alignItems: "center",
		elevation: 0,
		shadowColor: "#161616ff",
		shadowOpacity: 0,
		shadowRadius: 4,
		shadowOffset: { width: 0, height: 2 },
	},
});
