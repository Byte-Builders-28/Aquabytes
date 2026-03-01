// i18n.js
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Localization from "expo-localization";

// Translations
import en from "./locales/en.json";
import hi from "./locales/hi.json";
import ta from "./locales/ta.json";
import te from "./locales/te.json";
import ml from "./locales/ml.json";
import kn from "./locales/kn.json";
import mr from "./locales/mr.json";
import bn from "./locales/bn.json";
import asLang from "./locales/as.json";
import gu from "./locales/gu.json";
import pa from "./locales/pa.json";
import or from "./locales/or.json";
import ur from "./locales/ur.json";
import as from "./locales/as.json";
import ne from "./locales/ne.json";
import ks from "./locales/ks.json";
import kok from "./locales/kok.json";
import sa from "./locales/sa.json";
import sd from "./locales/sd.json";
import mai from "./locales/mai.json";
import brx from "./locales/brx.json";
import mni from "./locales/mni.json";
import sat from "./locales/sat.json";
import doi from "./locales/doi.json";

const LANGUAGE_KEY = "appLanguage";

const supportedLangs = [
	"en",
	"hi",
	"ta",
	"te",
	"ml",
	"kn",
	"mr",
	"bn",
	"as",
	"gu",
	"pa",
	"or",
	"ur",
	"ne",
	"ks",
	"kok",
	"sa",
	"sd",
	"mai",
	"brx",
	"mni",
	"sat",
	"doi",
];

const languageDetector = {
	type: "languageDetector",
	async: true,
	detect: async (cb) => {
		try {
			const savedLang = await AsyncStorage.getItem(LANGUAGE_KEY);
			if (savedLang && supportedLangs.includes(savedLang)) {
				cb(savedLang);
				return;
			}
			const deviceLang = Localization.locale.split("-")[0];
			cb(supportedLangs.includes(deviceLang) ? deviceLang : "en");
		} catch {
			cb("en");
		}
	},
	init: () => {},
	cacheUserLanguage: async (lng) => {
		try {
			await AsyncStorage.setItem(LANGUAGE_KEY, lng);
		} catch {}
	},
};

i18n
	.use(languageDetector)
	.use(initReactI18next)
	.init({
		compatibilityJSON: "v3",
		fallbackLng: "en",
		resources: {
			en: { translation: en },
			hi: { translation: hi },
			ta: { translation: ta },
			te: { translation: te },
			ml: { translation: ml },
			kn: { translation: kn },
			mr: { translation: mr },
			bn: { translation: bn },
			as: { translation: asLang },
			gu: { translation: gu },
			pa: { translation: pa },
			or: { translation: or },
			ur: { translation: ur },
			ne: { translation: ne },
			ks: { translation: ks },
			kok: { translation: kok },
			sa: { translation: sa },
			sd: { translation: sd },
			mai: { translation: mai },
			brx: { translation: brx },
			mni: { translation: mni },
			sat: { translation: sat },
			doi: { translation: doi },
		},
		interpolation: { escapeValue: false },
	});

// Manual language switch helper
export const changeLanguage = async (lng) => {
	if (!lng) return;
	try {
		await i18n.changeLanguage(lng);
		await AsyncStorage.setItem(LANGUAGE_KEY, lng);
	} catch (err) {
		console.error("Failed to change language:", err);
	}
};

export default i18n;
