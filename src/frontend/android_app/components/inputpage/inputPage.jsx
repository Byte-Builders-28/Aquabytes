import React from "react";
import { View, TouchableOpacity, Text } from "react-native";
import Question from "./questions";
import styles from "./styles";

export default function InputPage({
	currentPage,
	inputState,
	handleAnswer,
	getCityOptions,
	handleNext,
	totalPages,
}) {
	return (
		<View style={styles.card}>
			{currentPage.questions.map((q) => (
				<Question
					key={q.id}
					q={q}
					inputState={inputState}
					handleAnswer={handleAnswer}
					getCityOptions={getCityOptions}
				/>
			))}

			<TouchableOpacity style={styles.nextBtn} onPress={handleNext}>
				<Text style={styles.nextText}>
					{inputState.currentPage + 1 === totalPages ? "Submit" : "Next"}
				</Text>
			</TouchableOpacity>
		</View>
	);
}
