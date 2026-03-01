import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet, Image, BackHandler } from "react-native";
import { State, City } from "country-state-city";
import { useTranslation } from "react-i18next";
import AsyncStorage from "@react-native-async-storage/async-storage";

import InputPage from "../components/inputpage/inputPage";
import styles from "../components/inputpage/styles.js";
import OutputPage from "../components/output/output.jsx";
import WLoading from "../components/loading.jsx";
import Spacer from "../components/spacer.jsx";

import { readSavedLink } from "../utils/helpers.js";

export default function GetInput() {
	const { t } = useTranslation();

	const [InputState, setInputState] = useState({
		answers: {},
		completed: false,
	});
	const [pageStack, setPageStack] = useState([0]);
	const [serverResponse, setServerResponse] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);
	const countryCode = "IN";

	const pages = [
		{
			id: "page1",
			questions: [
				{
					id: "state",
					text: "questions.state.text",
					type: "dropdown",
					options: State.getStatesOfCountry(countryCode),
				},
				{
					id: "city",
					text: "questions.city.text",
					type: "dropdown",
					options: [],
				},
			],
		},
		{
			id: "page2",
			questions: [
				{
					id: "area",
					text: "questions.area.text",
					type: "input",
					placeholder: "questions.area.placeholder",
				},
				{
					id: "population",
					text: "questions.population.text",
					type: "input",
					placeholder: "questions.population.placeholder",
				},
			],
		},
		{
			id: "page3",
			questions: [
				{
					id: "roof",
					text: "questions.roof.text",
					type: "dropdown",
					options: [
						"questions.roof.options.concrete",
						"questions.roof.options.cementTiles",
						"questions.roof.options.clayTiles",
						"questions.roof.options.metalSheet",
						"questions.roof.options.giSheet",
						"questions.roof.options.asbestos",
						"questions.roof.options.slate",
						"questions.roof.options.stone",
						"questions.roof.options.corrugated",
						"questions.roof.options.thatched",
						"questions.roof.options.plastic",
						"questions.roof.options.glass",
						"questions.roof.options.green",
						"questions.roof.options.other",
					],
				},
			],
		},
		{
			id: "page4",
			questions: [
				{
					id: "budget",
					text: "questions.budget.text",
					type: "input",
					placeholder: "questions.budget.placeholder",
				},
			],
		},
	];

	const currentPageIndex = pageStack[pageStack.length - 1];
	const currentPage = pages[currentPageIndex];

	const handleAnswer = (id, value) => {
		const newAnswers = { ...InputState.answers, [id]: value };
		if (id === "state") newAnswers.city = "";
		setInputState((prev) => ({ ...prev, answers: newAnswers }));
	};

	const prepareAnswers = () => {
		const ans = { ...InputState.answers };
		if (ans.area) ans.area = parseFloat(ans.area);
		if (ans.population) ans.population = parseInt(ans.population, 10);
		if (ans.budget) ans.budget = parseFloat(ans.budget);
		return ans;
	};

	const submitSurvey = async () => {
		setLoading(true);
		try {
			const payload = prepareAnswers();
			console.log("Sending payload:", payload);

			const linkdata = await readSavedLink();
			const base_link = linkdata.currentLink;

			// Ensure URL ends with /
			const url = base_link.endsWith("/")
				? `${base_link}api/v1/rtwh/feasibility`
				: `${base_link}/api/v1/rtwh/feasibility`;

			console.log("Using URL:", url);

			const response = await fetch(url, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(payload),
			});

			const text = await response.text();
			console.log("Raw server response:", text);

			try {
				const data = JSON.parse(text);
				setServerResponse(data);
				setInputState((prev) => ({ ...prev, completed: true }));

				const newEntry = { timestamp: Date.now(), payload, response: data };
				const existingHistory = await AsyncStorage.getItem("surveyHistory");
				const history = existingHistory ? JSON.parse(existingHistory) : [];
				history.unshift(newEntry);
				await AsyncStorage.setItem("surveyHistory", JSON.stringify(history));
			} catch {
				console.error("Not valid JSON:", text);
			}
		} catch (error) {
			console.error("Error submitting survey:", error);
		} finally {
			setLoading(false);
		}
	};

	const handleNext = () => {
		const currentQuestions = pages[currentPageIndex].questions;

		for (let q of currentQuestions) {
			if (
				!InputState.answers[q.id] ||
				InputState.answers[q.id].toString().trim() === ""
			) {
				if (q.id !== "budget") {
					setError(t("getInput.errorFill", { field: t(q.text) }));
					return;
				}
			}
		}

		setError(null);

		if (currentPageIndex + 1 >= pages.length) {
			submitSurvey();
		} else {
			const nextPage = currentPageIndex + 1;
			setPageStack((prev) => [...prev, nextPage]);
		}
	};

	const stackBack = () => {
		if (pageStack.length > 1) setPageStack((prev) => prev.slice(0, -1));
	};

	const getCityOptions = () => {
		const stateName = InputState.answers["state"];
		if (!stateName) return [];
		const stateObj = State.getStatesOfCountry(countryCode).find(
			(s) => s.name === stateName,
		);
		return stateObj ? City.getCitiesOfState(countryCode, stateObj.isoCode) : [];
	};

	useEffect(() => {
		const backHandler = BackHandler.addEventListener(
			"hardwareBackPress",
			() => {
				if (pageStack.length > 1) {
					stackBack();
					return true;
				}
				return false;
			},
		);

		return () => backHandler.remove();
	}, [pageStack]);

	return (
		<View style={styles.container}>
			{loading ? (
				<View style={styles.completed}>
					<WLoading />
				</View>
			) : !InputState.completed ? (
				<>
					<Text style={styles.header}>{t("getInput.header")}</Text>
					<Spacer height={60} />
					<Image source={require("../assets/water.png")} style={styles.image} />
					<Spacer height={20} />

					<InputPage
						currentPage={currentPage}
						inputState={InputState}
						handleAnswer={handleAnswer}
						getCityOptions={getCityOptions}
						handleNext={handleNext}
						totalPages={pages.length}
					/>

					{error && (
						<Text style={{ color: "red", marginTop: 10, textAlign: "center" }}>
							{error}
						</Text>
					)}
				</>
			) : (
				<OutputPage response={serverResponse} />
			)}
		</View>
	);
}
