import React from "react";
import { View, Text, TextInput } from "react-native";
import { Picker } from "@react-native-picker/picker";
import { useTranslation } from "react-i18next";
import styles from "./styles";

export default function Question({
	q,
	inputState,
	handleAnswer,
	getCityOptions,
}) {
	const { t } = useTranslation();

	return (
		<View style={{ marginBottom: 20 }}>
			{/* Question Text */}
			<Text style={styles.question}>{t(q.text)}</Text>

			{/* Dropdown */}
			{q.type === "dropdown" && (
				<Picker
					style={[{ color: "#1e1e1eff" }, styles.input]}
					selectedValue={inputState.answers[q.id] || ""}
					onValueChange={(val) => handleAnswer(q.id, val)}>
					<Picker.Item label={t("question.selectOption")} value="" />

					{/* State */}
					{q.id === "state" &&
						q.options.map((opt) => (
							<Picker.Item
								key={opt.isoCode}
								label={opt.name}
								value={opt.name}
							/>
						))}

					{/* City */}
					{q.id === "city" &&
						getCityOptions().map((opt) => (
							<Picker.Item key={opt.name} label={opt.name} value={opt.name} />
						))}

					{/* Other dropdowns */}
					{q.id !== "state" &&
						q.id !== "city" &&
						q.options.map((opt) => (
							<Picker.Item
								key={t(opt, { lng: "en" })}
								label={t(opt)}
								value={t(opt, { lng: "en" })}
							/>
						))}
				</Picker>
			)}

			{/* Input */}
			{q.type === "input" && (
				<TextInput
					style={styles.input}
					placeholder={t(q.placeholder || "")}
					value={inputState.answers[q.id] || ""}
					onChangeText={(val) => handleAnswer(q.id, val)}
				/>
			)}
			{q.id === "budget" && (
				<View style={styles.hintCard}>
					<Text style={styles.hintText}>
						For a 500L tank, it will cost around 5000 Rs.
					</Text>
				</View>
			)}
		</View>
	);
}
