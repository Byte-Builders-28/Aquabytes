import React, { useState } from "react";
import {
	View,
	Image,
	StyleSheet,
	Modal,
	Text,
	TouchableOpacity,
	FlatList,
	SectionList,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import i18n from "../i18n";

export default function Header() {
	const [modalVisible, setModalVisible] = useState(false);
	const [selectedLang, setSelectedLang] = useState(i18n.language);

	const languages = [
		{ code: "en", label: "English" }, // English
		{ code: "as", label: "অসমীয়া" }, // Assamese
		{ code: "bn", label: "বাংলা" }, // Bengali
		{ code: "brx", label: "बरो" }, // Bodo - TODO
		{ code: "doi", label: "डोगरी" }, // Dogri
		{ code: "gu", label: "ગુજરાતી" }, // Gujarati
		{ code: "hi", label: "हिन्दी" }, // Hindi
		{ code: "kn", label: "ಕನ್ನಡ" }, // Kannada
		{ code: "ks", label: "कश्मीरी" }, // Kashmiri - TODO
		{ code: "kok", label: "कोंकणी" }, // Konkani - TODO
		{ code: "mai", label: "मैथिली" }, // Maithili - TODO
		{ code: "ml", label: "മലയാളം" }, // Malayalam
		{ code: "mni", label: "মেইতেই লোন্" }, // Manipuri (Meitei)
		{ code: "mr", label: "मराठी" }, // Marathi
		{ code: "ne", label: "नेपाली" }, // Nepali
		{ code: "or", label: "ଓଡ଼ିଆ" }, // Odia
		{ code: "pa", label: "ਪੰਜਾਬੀ" }, // Punjabi
		{ code: "sa", label: "संस्कृतम्" }, // Sanskrit
		{ code: "sat", label: "ᱥᱟᱱᱛᱟᱲᱤ" }, // Santali (Ol Chiki)
		{ code: "sd", label: "سنڌي" }, // Sindhi
		{ code: "ta", label: "தமிழ்" }, // Tamil
		{ code: "te", label: "తెలుగు" }, // Telugu
		{ code: "ur", label: "اردو" }, // Urdu
	];

	// Group languages alphabetically
	const groupedLanguages = Object.values(
		languages.reduce((acc, lang) => {
			const letter = lang.label[0].toUpperCase();
			if (!acc[letter]) acc[letter] = { title: letter, data: [] };
			acc[letter].data.push(lang);
			return acc;
		}, {})
	).sort((a, b) => a.title.localeCompare(b.title));

	const changeLanguage = (lang) => {
		setSelectedLang(lang);
		i18n.changeLanguage(lang).catch((err) => console.error(err));
		setModalVisible(false);
	};

	return (
		<View style={styles.header}>
			<View style={styles.headerRow}>
				<Image
					source={{ uri: "https://i.pravatar.cc/155" }}
					style={styles.avatar}
				/>
				<TouchableOpacity onPress={() => setModalVisible(true)}>
					<Ionicons name="globe-outline" size={28} color="white" />
				</TouchableOpacity>
			</View>

			<Modal
				visible={modalVisible}
				transparent
				animationType="slide"
				onRequestClose={() => setModalVisible(false)}>
				<TouchableOpacity
					style={styles.modalOverlay}
					activeOpacity={1}
					onPressOut={() => setModalVisible(false)}>
					<View style={styles.modalContent}>
						<Text style={styles.modalHeader}>Select Language</Text>

						<SectionList
							sections={groupedLanguages}
							keyExtractor={(item) => item.code}
							renderItem={({ item }) => (
								<TouchableOpacity
									style={styles.langItem}
									onPress={() => changeLanguage(item.code)}>
									<Text
										style={{
											fontWeight:
												selectedLang === item.code ? "bold" : "normal",
											fontSize: 16,
										}}>
										{item.label}
									</Text>
								</TouchableOpacity>
							)}
							renderSectionHeader={({ section: { title } }) => (
								<Text style={styles.sectionHeader}>{title}</Text>
							)}
							showsVerticalScrollIndicator={false}
						/>
					</View>
				</TouchableOpacity>
			</Modal>
		</View>
	);
}

const styles = StyleSheet.create({
	header: {
		backgroundColor: "transparent",
		paddingVertical: 40,
		paddingHorizontal: 20,
	},
	headerRow: {
		flexDirection: "row",
		justifyContent: "space-between",
		alignItems: "center",
	},
	avatar: {
		width: 40,
		height: 40,
		borderRadius: 20,
	},
	modalOverlay: {
		flex: 1,
		backgroundColor: "rgba(0,0,0,0.4)",
		justifyContent: "center",
		alignItems: "center",
		paddingHorizontal: 20,
	},
	modalContent: {
		width: "100%",
		maxHeight: "70%",
		backgroundColor: "#fff",
		borderRadius: 12,
		padding: 20,
	},
	modalHeader: {
		fontSize: 18,
		fontWeight: "700",
		marginBottom: 12,
		textAlign: "center",
	},
	sectionHeader: {
		fontSize: 14,
		fontWeight: "700",
		backgroundColor: "#f0f0f0",
		paddingVertical: 4,
		paddingHorizontal: 10,
		marginTop: 10,
		borderRadius: 4,
	},
	langItem: {
		paddingVertical: 10,
		paddingHorizontal: 10,
		borderBottomWidth: 0.5,
		borderBottomColor: "#ccc",
	},
});
