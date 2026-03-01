import React from "react";
import { SafeAreaView, ScrollView, StyleSheet } from "react-native";
import Header from "../components/header";
import StartCard from "../components/getStartedCard";

import InfoSection from "../components/homeInfo";
import BottomNav from "../components/bottomNav";
import WaterRiskCheck from "../components/waterRiskCheck";
import Spacer from "../components/spacer";

// import LoadingScreen from "../components/loading";

import { Image } from "react-native";

export default function home() {
	return (
		<SafeAreaView style={styles.container}>
			<Image
				source={require("../assets/background.png")}
				style={styles.backgroundImage}
				resizeMode="cover"
			/>
			<ScrollView showsVerticalScrollIndicator={false}>
				<Header />
				<Spacer height={20}></Spacer>
				<StartCard />
				<Spacer height={20}></Spacer>
				<WaterRiskCheck />
				<InfoSection />
			</ScrollView>
			<Spacer height={25}></Spacer>
			<BottomNav />
		</SafeAreaView>
	);
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: "#fffafa",
	},
	backgroundImage: {
		...StyleSheet.absoluteFillObject, // fills the entire parent
		zIndex: 0, // behind everything
	},
});
