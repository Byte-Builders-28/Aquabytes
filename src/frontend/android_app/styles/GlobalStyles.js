import { StyleSheet } from "react-native";

export const styles = StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: "#fff",
	},
	scrollContainer: {
		padding: 20,
		paddingBottom: 40,
	},
	header: {
		flexDirection: "row",
		justifyContent: "space-between",
		alignItems: "center",
		paddingHorizontal: 20,
		paddingTop: 50,
		paddingBottom: 10,
		backgroundColor: "#f8f8f8",
		borderBottomWidth: 1,
		borderBottomColor: "#eee",
	},
	time: {
		fontSize: 16,
		fontWeight: "bold",
	},
	headerIcons: {
		flexDirection: "row",
	},
	iconPlaceholder: {
		width: 20,
		height: 20,
		backgroundColor: "#ddd",
		borderRadius: 10,
		marginLeft: 5,
	},
	section: {
		marginBottom: 25,
	},
	sectionTitle: {
		fontSize: 18,
		fontWeight: "bold",
		marginBottom: 15,
		color: "#333",
	},
	inputContainer: {
		marginBottom: 15,
	},
	label: {
		fontSize: 16,
		marginBottom: 5,
		color: "#555",
	},
	input: {
		borderWidth: 1,
		borderColor: "#ddd",
		borderRadius: 8,
		padding: 12,
		fontSize: 16,
	},
	uploadButton: {
		backgroundColor: "#4a86e8",
		padding: 15,
		borderRadius: 8,
		alignItems: "center",
	},
	uploadButtonText: {
		color: "white",
		fontSize: 16,
		fontWeight: "bold",
	},
	previewImage: {
		width: "100%",
		height: 200,
		marginTop: 15,
		borderRadius: 8,
	},
	button: {
		backgroundColor: "#245BCA",
		padding: 18,
		paddingHorizontal: 18,
		borderRadius: 8,
		alignItems: "center",
		marginTop: 10,
	},
	buttonText: {
		color: "white",
		fontSize: 18,
		fontWeight: "bold",
	},
});
