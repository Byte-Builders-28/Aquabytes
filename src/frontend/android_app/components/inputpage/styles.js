import { StyleSheet } from "react-native";

export default StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: "#fffafa",
		alignItems: "center",
		padding: 20,
	},
	header: { fontSize: 22, fontWeight: "bold", marginTop: 20 },
	image: { width: 120, height: 120, marginVertical: 15, resizeMode: "contain" },
	card: {
		width: "100%",
		padding: 20,
		borderRadius: 12,
		backgroundColor: "#E9F3FF",
		marginBottom: 15,
	},
	question: { fontSize: 16, fontWeight: "500", marginBottom: 8 },
	input: {
		borderWidth: 1,
		borderColor: "#ccc",
		borderRadius: 8,
		padding: 10,
		backgroundColor: "#aecceeff",
	},
	nextBtn: {
		backgroundColor: "#007AFF",
		padding: 15,
		borderRadius: 12,
		alignItems: "center",
		marginTop: 10,
	},
	nextText: { color: "#fffafa", fontSize: 16, fontWeight: "600" },
	completed: { flex: 1, justifyContent: "center", alignItems: "center" },
	done: { fontSize: 20, fontWeight: "bold", marginBottom: 10 },
	hintCard: {
		marginTop: 6,
		padding: 10,
		backgroundColor: "#e0f7fa", // light teal for card-like feel
		borderRadius: 10,
		borderWidth: 1,
		borderColor: "#b2ebf2",
	},
	hintText: {
		fontSize: 13,
		color: "#00796b",
		fontStyle: "italic",
	},
});
