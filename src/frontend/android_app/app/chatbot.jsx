import React, { useState, useRef, useEffect } from "react";
import {
	View,
	Text,
	TextInput,
	TouchableOpacity,
	ScrollView,
	StyleSheet,
	Image,
	KeyboardAvoidingView,
	Platform,
	TouchableWithoutFeedback,
	Keyboard,
	SafeAreaView,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Ionicons } from "@expo/vector-icons";
import { askGemini } from "../utils/chatbot";

export default function ChatbotScreen() {
	const [input, setInput] = useState("");
	const [messages, setMessages] = useState([]);
	const [latestSurvey, setLatestSurvey] = useState(null);
	const scrollViewRef = useRef();

	// --- Base system prompt ---
	const basePrompt =
		"You are Elsa, a chatbot specialized ONLY in Roof Water Harvesting. " +
		"If the user asks about water harvesting, tanks, recharge, feasibility, or related topics, answer clearly. " +
		
		"Always respond in the same language the user used in their question.";

	// --- Load survey cache + init bot message ---
	useEffect(() => {
		(async () => {
			try {
				// Load latest survey cache
				const savedSurvey = await AsyncStorage.getItem("surveyHistory");
				if (savedSurvey) {
					const parsed = JSON.parse(savedSurvey);
					if (parsed.length > 0) {
						setLatestSurvey(parsed[0]); // newest entry
					}
				}
			} catch (e) {
				console.error("⚠️ Failed to load survey cache:", e);
			}

			// Init chatbot messages
			setMessages([
				{
					sender: "Bot",
					text: "Hi, I am Elsa 😊. How can I assist you with Roof Water Harvesting today?",
				},
			]);
		})();
	}, []);

	const handleSend = async () => {
		if (!input.trim()) return;

		const userMsg = { sender: "You", text: input };
		setMessages((prev) => [...prev, userMsg]);
		setInput("");

		// Temporary "typing" message
		setMessages((prev) => [...prev, { sender: "Bot", text: "..." }]);

		try {
			// Add survey response context
			const surveyContext = latestSurvey
				? `\nHere is the latest feasibility calculation result (JSON): ${JSON.stringify(
						latestSurvey.response
				  )}`
				: "";

			const fullPrompt = `${basePrompt}${surveyContext}\nUser: ${input}\nBot:`;

			const reply = await askGemini(fullPrompt);

			setMessages((prev) => [
				...prev.slice(0, -1),
				{ sender: "Bot", text: reply },
			]);
		} catch (err) {
			console.error("⚠️ Chatbot error:", err);
			setMessages((prev) => [
				...prev.slice(0, -1),
				{ sender: "Bot", text: "⚠️ Error fetching reply" },
			]);
		}
	};

	return (
		<SafeAreaView style={{ flex: 1 }}>
			<KeyboardAvoidingView
				style={{ flex: 1 }}
				behavior={Platform.OS === "ios" ? "padding" : "height"}
				keyboardVerticalOffset={Platform.OS === "ios" ? 80 : 0}>
				<TouchableWithoutFeedback onPress={Keyboard.dismiss}>
					<View style={styles.container}>
						{/* Messages */}
						<ScrollView
							style={styles.chatBox}
							ref={scrollViewRef}
							onContentSizeChange={() =>
								scrollViewRef.current.scrollToEnd({ animated: true })
							}>
							{messages.map((msg, i) => (
								<View
									key={i}
									style={[
										styles.row,
										msg.sender === "You" ? styles.userRow : styles.botRow,
									]}>
									{/* Bot Avatar */}
									{msg.sender === "Bot" ? (
										<Image
											source={{
												uri: "https://img.icons8.com/emoji/48/robot-emoji.png",
											}}
											style={styles.avatar}
										/>
									) : null}

									{/* Message bubble */}
									<View
										style={[
											styles.msgBubble,
											msg.sender === "You"
												? styles.userBubble
												: styles.botBubble,
										]}>
										<Text style={styles.msgText}>{msg.text}</Text>
									</View>

									{/* User Avatar */}
									{msg.sender === "You" ? (
										<View style={styles.userAvatar}>
											<Text style={styles.userInitial}>U</Text>
										</View>
									) : null}
								</View>
							))}
						</ScrollView>

						{/* Input */}
						<View style={styles.inputRow}>
							<TextInput
								style={styles.input}
								value={input}
								onChangeText={setInput}
								placeholder="Message Elsa"
							/>
							<TouchableOpacity style={styles.sendBtn} onPress={handleSend}>
								<Ionicons name="arrow-up-circle" size={30} color="#7b5cff" />
							</TouchableOpacity>
						</View>
					</View>
				</TouchableWithoutFeedback>
			</KeyboardAvoidingView>
		</SafeAreaView>
	);
}

const styles = StyleSheet.create({
	container: { flex: 1, backgroundColor: "#fff" },
	chatBox: { flex: 1, padding: 10 },
	row: {
		flexDirection: "row",
		alignItems: "flex-end",
		marginVertical: 4,
	},
	botRow: { justifyContent: "flex-start" },
	userRow: { justifyContent: "flex-end" },

	avatar: { width: 32, height: 32, borderRadius: 16, marginRight: 5 },
	userAvatar: {
		width: 32,
		height: 32,
		borderRadius: 16,
		backgroundColor: "#1a73e8",
		alignItems: "center",
		justifyContent: "center",
		marginLeft: 5,
	},
	userInitial: { color: "#fff", fontWeight: "bold" },

	msgBubble: {
		padding: 10,
		borderRadius: 15,
		maxWidth: "70%",
	},
	botBubble: {
		backgroundColor: "#bdf5a5ff",
		borderTopLeftRadius: 0,
	},
	userBubble: {
		backgroundColor: "#8dbdf0ff",
		borderTopRightRadius: 0,
	},
	msgText: { fontSize: 15 },

	inputRow: {
		flexDirection: "row",
		alignItems: "center",
		borderTopWidth: 1,
		borderColor: "#eee",
		padding: 8,
	},
	input: {
		flex: 1,
		borderWidth: 1,
		borderColor: "#ddd",
		borderRadius: 20,
		paddingHorizontal: 12,
		marginRight: 8,
	},
	sendBtn: { padding: 2 },
});
