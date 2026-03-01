import { GoogleGenerativeAI } from "@google/generative-ai";

const API_KEY = process.env.EXPO_PUBLIC_GEMINI_API_KEY;

const genAI = new GoogleGenerativeAI("{KEY ADDED VIA ENV NOT IN REPO}");

export async function askGemini(prompt) {
	try {
		const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash-lite" });
		const result = await model.generateContent(prompt);
		return result.response.text();
	} catch (error) {
		console.error("Chatbot Error:", error);
		return "Sorry, something went wrong with the chatbot.";
	}
}
