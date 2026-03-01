import React from "react";
import {
	View,
	Text,
	Image,
	StyleSheet,
	ScrollView,
	Linking,
} from "react-native";

export default function InfoSection() {
	const handlePress = (url) => {
		Linking.openURL(url).catch((err) =>
			console.error("Failed to open URL:", err)
		);
	};

	return (
		<View style={styles.section}>
			<View style={styles.sectionHeader}>
				<Text style={styles.sectionTitle}>INFO</Text>
			</View>

			<ScrollView
				horizontal
				showsHorizontalScrollIndicator={false}
				contentContainerStyle={styles.cardRow}>
				{/* Blog Post 1 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress(
							"https://nwm.gov.in/sites/default/files/IS-15797-Rainwater_Haresting_Roof_Top.pdf"
						)
					}>
					<Image
						source={{
							uri: "https://t3.ftcdn.net/jpg/16/80/32/60/240_F_1680326024_IyX91mjuqCyr4A8QPFtLDsmP7nHg36Dj.jpg",
						}}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>
						IS 15797: Rooftop Rainwater Harvesting Guidelines
					</Text>
					<Text style={styles.infoSubtitle}>National Water Mission</Text>
				</View>

				{/* Blog Post 2 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress(
							"https://www.pib.gov.in/PressReleasePage.aspx?PRID=1914351"
						)
					}>
					<Image
						source={{
							uri: "https://t3.ftcdn.net/jpg/16/90/28/56/240_F_1690285611_9tuRrsOpRbUILhMGtPxpe1qbappuzIBl.jpg",
						}}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>Policy for Rainwater Harvesting</Text>
					<Text style={styles.infoSubtitle}>Press Information Bureau</Text>
				</View>

				{/* Blog Post 3 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress("https://www.cgwb.gov.in/en/stories-blog")
					}>
					<Image
						source={{ uri: "https://t4.ftcdn.net/jpg/14/86/13/77/240_F_1486137700_ElpdOasWiFe96rZZEMfkjcN3rnrV22GY.jpg" }}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>
						Ground Water Harvesting Best Practices in Telangana
					</Text>
					<Text style={styles.infoSubtitle}>Central Ground Water Board</Text>
				</View>

				{/* Blog Post 4 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress(
							"https://www.twadboard.tn.gov.in/roof-top-rain-water-harvesting-rrwh"
						)
					}>
					<Image
						source={{
							uri: "https://t4.ftcdn.net/jpg/15/44/60/33/240_F_1544603397_eLWunVDjQCsxvml2woUwlPVbjKosB8dh.jpg",
						}}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>
						Roof Top Rain Water Harvesting (RRWH)
					</Text>
					<Text style={styles.infoSubtitle}>
						Tamil Nadu Water Supply and Drainage Board
					</Text>
				</View>

				{/* Blog Post 5 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress(
							"https://www.nwm.gov.in/sites/default/files/RWH_Structures_final.pdf"
						)
					}>
					<Image
						source={{
							uri: "https://t4.ftcdn.net/jpg/14/83/89/57/240_F_1483895740_lQliOSrcZ1wsfiApEClkp4SaWQFQaZ01.jpg",
						}}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>
						General Guidelines on Rainwater Harvesting Structures
					</Text>
					<Text style={styles.infoSubtitle}>National Water Mission</Text>
				</View>

				{/* Blog Post 6 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress("https://www.mppcb.mp.gov.in/RWH.aspx")
					}>
					<Image
						source={{ uri: "https://t3.ftcdn.net/jpg/16/70/56/42/240_F_1670564205_JxlK59OFl6zkynQ4JhyT5IPYl6m3nGnC.jpg" }}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>
						Methods of Roof Top Rainwater Harvesting
					</Text>
					<Text style={styles.infoSubtitle}>
						Madhya Pradesh Pollution Control Board
					</Text>
				</View>

				{/* Blog Post 7 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress(
							"https://www.delhijalboard.delhi.gov.in/doit/tab-content/rain-water-harvesting?page=1"
						)
					}>
					<Image
						source={{
							uri: "https://t3.ftcdn.net/jpg/14/81/41/00/240_F_1481410057_qXyflpBuxBM0vK3epn98LCRDqd9MdeFB.jpg",
						}}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>
						Rain Water Harvesting | Delhi Jal Board
					</Text>
					<Text style={styles.infoSubtitle}>Delhi Jal Board</Text>
				</View>

				{/* Blog Post 8 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress("https://echhata.odisha.gov.in/about.php")
					}>
					<Image
						source={{ uri: "https://t4.ftcdn.net/jpg/14/86/30/89/240_F_1486308959_zxr1FRaKT9gGwqO1YbxGdfgCf1yR2nWJ.jpg" }}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>
						CHHATA: Odisha's Rooftop Rainwater Harvesting Scheme
					</Text>
					<Text style={styles.infoSubtitle}>Odisha Government</Text>
				</View>

				{/* Blog Post 9 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress(
							"https://www.nwm.gov.in/sites/default/files/IS-15797-Rainwater_Haresting_Roof_Top.pdf"
						)
					}>
					<Image
						source={{
							uri: "https://t3.ftcdn.net/jpg/12/97/81/02/240_F_1297810260_wLUcDCxjjKRx6qsJtzT66AwFfQgnUy6L.jpg",
						}}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>
						IS 15797: Rooftop Rainwater Harvesting Guidelines
					</Text>
					<Text style={styles.infoSubtitle}>National Water Mission</Text>
				</View>

				{/* Blog Post 10 */}
				<View
					style={styles.infoCard}
					onTouchEnd={() =>
						handlePress(
							"https://www.pib.gov.in/PressReleasePage.aspx?PRID=1914351"
						)
					}>
					<Image
						source={{
							uri: "https://t4.ftcdn.net/jpg/14/08/49/05/240_F_1408490542_Qg0rZcsrpiIOEYHhN950htuwUKsyC4wR.jpg",
						}}
						style={styles.infoImage}
					/>
					<Text style={styles.infoTitle}>Policy for Rainwater Harvesting</Text>
					<Text style={styles.infoSubtitle}>Press Information Bureau</Text>
				</View>
			</ScrollView>
		</View>
	);
}

const styles = StyleSheet.create({
	section: {
		marginTop: 20,
		paddingHorizontal: 20,
	},
	sectionHeader: {
		flexDirection: "row",
		justifyContent: "space-between",
		marginBottom: 10,
	},
	sectionTitle: {
		fontWeight: "bold",
		color: "#333",
	},
	sectionMore: {
		color: "#2563eb",
		fontWeight: "600",
	},
	cardRow: {
		gap: 15, // space between cards
	},
	infoCard: {
		width: 180,
		cursor: "pointer",
	},
	infoImage: {
		width: "100%",
		height: 100,
		borderRadius: 10,
	},
	infoTitle: {
		marginTop: 8,
		fontWeight: "600",
		fontSize: 14,
	},
	infoSubtitle: {
		fontSize: 12,
		color: "#666",
	},
});
