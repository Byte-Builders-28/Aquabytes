// app/_layout.js
import { Stack } from "expo-router";
import { I18nextProvider } from "react-i18next";
import React, { useEffect, useState } from "react";
import i18n from "../i18n";
import LoadingScreen from "../components/loading";
import { fetchAndSaveLink } from "../utils/helpers";

import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";

export default function Layout() {
	const [ready, setReady] = useState(false);

	useEffect(() => {
		async function init() {
			// fetch + overwrite on every app start, fallback if needed
			await fetchAndSaveLink("XpolioN2005", "backend-link", "link.json");
			setReady(true);
		}
		init();
	}, []);

	if (!ready) {
		return <LoadingScreen />;
	}

	return (
		<I18nextProvider i18n={i18n}>
			<SafeAreaProvider>
				<SafeAreaView
					style={{ flex: 1, backgroundColor: "#fff" }}
					edges={["top", "bottom"]}>
					<Stack screenOptions={{ headerShown: false }} />
				</SafeAreaView>
			</SafeAreaProvider>
		</I18nextProvider>
	);
}
