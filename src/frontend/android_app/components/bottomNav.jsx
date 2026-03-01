import React, { useState } from "react";
import { View, StyleSheet, TouchableOpacity } from "react-native";
import { MaterialIcons } from "@expo/vector-icons";
import { useNavigation } from "@react-navigation/native";

export default function BottomNav() {
	const navigation = useNavigation();
	const [active, setActive] = useState("home");

	const navItems = [
		{ name: "home", route: "index" },
		{ name: "history", route: "history" },
		{ name: "group", route: "404" },
		// { name: "settings", route: "SettingsScreen" },
	];

	return (
		<View style={styles.bottomNav}>
			{navItems.map((item) => (
				<TouchableOpacity
					key={item.name}
					onPress={() => {
						setActive(item.name);
						navigation.navigate(item.route);
					}}>
					<MaterialIcons
						name={item.name}
						size={26}
						color={active === item.name ? "#2563eb" : "gray"}
					/>
				</TouchableOpacity>
			))}
		</View>
	);
}

const styles = StyleSheet.create({
	bottomNav: {
		flexDirection: "row",
		justifyContent: "space-around",
		paddingVertical: 12,
		borderTopWidth: 1,
		borderColor: "#ddd",
		backgroundColor: "#fff",
	},
});
