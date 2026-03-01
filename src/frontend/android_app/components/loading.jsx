import React, { useRef, useEffect } from "react";
import {
	View,
	StyleSheet,
	Text,
	Linking,
	TouchableOpacity,
	Animated,
} from "react-native";
import { Image } from "expo-image";

export default function LoadingScreen() {
	return (
		<View style={styles.container}>
			<Animated.View>
				<Image
					source={require("../assets/loading.gif")}
					style={styles.gif}
					contentFit="contain"
					placeholder={null}
					autoplay
				/>
			</Animated.View>

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
	},
	gif: {
		width: 100,
		height: 100,
	},
	attribution: {
		position: "absolute",
		bottom: 50,
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
