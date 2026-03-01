import AsyncStorage from "@react-native-async-storage/async-storage";

const LINK_KEY = "currentLinkData";

/**
 * Fetch from GitHub. If fails, fallback to last saved AsyncStorage value.
 */
export async function fetchAndSaveLink(owner, repo, filepath, branch = "main") {
  const url = `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${filepath}`;

  try {
    const response = await fetch(url, { cache: "no-store" }); // force fresh
    if (!response.ok) throw new Error(`Failed to fetch: ${response.status}`);

    const data = await response.json();

    // 🔥 always overwrite with new data
    await AsyncStorage.setItem(LINK_KEY, JSON.stringify(data));

    return data;
  } catch (err) {
    console.warn("GitHub fetch failed, using cached value:", err);

    // fallback to last saved
    const saved = await readSavedLink();
    return saved;
  }
}

/**
 * Read from AsyncStorage (null if missing/invalid).
 */
export async function readSavedLink() {
  try {
    const value = await AsyncStorage.getItem(LINK_KEY);
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
      }
