import React from "react";
import {
	View,
	StyleSheet,
	Text,
	Linking,
	TouchableOpacity,
} from "react-native";
import { Image } from "expo-image";

export default function NotFoundScreen() {
	return (
		<View style={styles.container}>
			<Image
				source={require("../assets/404.png")}
				style={styles.gif}
				contentFit="contain"
				placeholder={null}
				autoplay
			/>

			<Text style={styles.title}>🚧 This page is under construction 🚧</Text>
			<Text style={styles.subtitle}>
				We're working hard to bring you this feature soon!
			</Text>

			<View style={styles.attribution}>
				<Text style={styles.text}>Icons by </Text>
				<TouchableOpacity
					onPress={() => Linking.openURL("https://lordicon.com")}>
					<Text style={styles.link}>Lordicon</Text>
				</TouchableOpacity>
			</View>
		</View>
	);
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		justifyContent: "center",
		alignItems: "center",
		backgroundColor: "#fff",
		paddingHorizontal: 20,
	},
	gif: {
		width: 150,
		height: 150,
		marginBottom: 20,
	},
	title: {
		fontSize: 18,
		fontWeight: "bold",
		textAlign: "center",
		color: "#333",
		marginBottom: 8,
	},
	subtitle: {
		fontSize: 14,
		textAlign: "center",
		color: "#666",
		marginBottom: 40,
	},
	attribution: {
		position: "absolute",
		bottom: 20,
		flexDirection: "row",
		alignItems: "center",
	},
	text: {
		fontSize: 10,
		color: "#aaa",
	},
	link: {
		fontSize: 10,
		color: "#aaa",
		textDecorationLine: "underline",
	},
});
