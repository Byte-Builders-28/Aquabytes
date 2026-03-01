import React from "react";
import { View, Text } from "react-native";
import styles from "./styles";

export default function ResponseView({ serverResponse }) {
	return (
		<View style={styles.completed}>
			<Text style={styles.done}>🎉 Server Response!</Text>
			<Text>{JSON.stringify(serverResponse, null, 2)}</Text>
		</View>
	);
}
