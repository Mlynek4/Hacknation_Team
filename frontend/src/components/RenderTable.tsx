import { MdOutlineAutoAwesome } from "react-icons/md";
import { typography } from "../constants/typography";
import { css, cx } from "@emotion/css";
import colorPalette from "../constants/colorPalette";
import { useEffect, useState } from "react";
import RunButton from "./RunButton";
import { chatApi } from "@/api/chatApi";
import Skeleton, { SkeletonTheme } from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";

const Header = ({ header, description }) => {
  return (
    <div
      className={cx(
        "header-border-right",
        css`
          display: flex;
          flex-direction: column;
          gap: 5px;
          width: 100%;

          border-bottom: 1px solid ${colorPalette.strokePrimary};
          padding: 10px 15px;
        `
      )}
    >
      <p className={typography.textLPlus}>{header}</p>
      <span
        className={cx(
          typography.textXsPlus,
          css`
            color: ${colorPalette.textSecondary};
          `
        )}
      >
        {description}
      </span>
    </div>
  );
};

const OutputTextArea = ({ value, onChange, readOnly = false }) => {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange && onChange(e.target.value)}
      className={cx(
        "output-border-right",
        css`
          width: 100%;
          height: 100%;
          border: none;
          resize: none;
          font-size: 14px;
          background-color: ${colorPalette.background};
          color: ${colorPalette.primary};

          cursor: ${readOnly ? "not-allowed" : "text"};
          &:focus {
            outline: none;
          }
        `
      )}
      readOnly={readOnly}
    ></textarea>
  );
};

const PLACEHOLDER_REGEX = /\[.*?\]/g;
const VIBRANT_BORDER_COLORS = [
  "#FF4444",
  "#33B5E5",
  "#99CC00",
  "#FFBB33",
  "#CC00CC",
  "#00DDFF",
];

const PII_COLOR_MAP = {
  // 1. DANE IDENTYFIKACYJNE OSOBOWE (25% Zwiększona Saturaacja i Jasność)

  // -- Podstawowa identyfikacja (Błękity, Cyjany, Jasne Zielenie)
  name: "#00FFFF", // Czysty Cyjan
  surname: "#00BFFF", // Głęboki Błękit
  age: "#7FFF00", // Jasna Zieleń Chartreuse
  "date-of-birth": "#32CD32", // Limonkowa Zieleń
  date: "#ADFF2F", // Żółto-Zielony
  relative: "#00FA9A", // Wiosenna Zieleń

  // -- Dane Wrażliwe (Czerwienie, Magnety, Fiolety - Wyróżnienie)
  sex: "#FF4500", // Pomarańczowo-Czerwony
  religion: "#FF1493", // Intensywny Róż (Deep Pink)
  "political-view": "#FF00FF", // Magenta
  ethnicity: "#9932CC", // Fiolet Orchid
  "sexual-orientation": "#8A2BE2", // Fiolet Niebieski
  health: "#DC143C", // Karmazynowy (Mocna Czerwień)

  // 2. DANE KONTAKTOWE I LOKALIZACYJNE (Żółcie, Złota)
  city: "#FFFF00", // Czysty Żółty
  address: "#FFD700", // Złoty
  email: "#FFA500", // Pomarańczowy
  phone: "#FF8C00", // Ciemny Pomarańcz

  // 3. IDENTYFIKATORY DOKUMENTÓW (Krytyczne - Czerwone i Pomarańczowe Odcienie)
  pesel: "#FF0000", // Czysta Czerwień (Max Alarm)
  "document-number": "#FF69B4", // Gorący Róż (Hot Pink)

  // 4. DANE ZAWODOWE I EDUKACYJNE (Zieleń, Turkus)
  company: "#00FF7F", // Wiosenny Turkus
  "school-name": "#40E0D0", // Turkus
  "job-title": "#00CED1", // Ciemny Turkus

  // 5. INFORMACJE FINANSOWE (Fiolety i Indygo)
  "bank-account": "#800080", // Fiolet
  "credit-card-number": "#4B0082", // Indygo

  // 6. IDENTYFIKATORY CYFROWE I LOGINY (Brązy, Ciemne Złota)
  username: "#DAA520", // Złoty Pręt (Goldenrod)
  secret: "#B8860B", // Ciemne Złoto (DarkGoldenrod)
};

const getRandomItem = (arr) => arr[Math.floor(Math.random() * arr.length)];

const tokenizeAndStyleText = (text) => {
  // Użycie metody .replace z funkcją callback do utworzenia elementu <span>
  const styledText = text.replace(PLACEHOLDER_REGEX, (matchedToken) => {
    console.log("matchedToken", matchedToken);
    // Używamy `className` 'token' do zastosowania stylów CSS
    const key = matchedToken.slice(1, -1).toLowerCase(); // Usuń nawiasy kwadratowe i zamień na małe litery
    console.log("key", key);

    const randomBgColor = PII_COLOR_MAP[key] ?? "#888888";
    // const randomBgColor = VIBRANT_BORDER_COLORS[i % VIBRANT_BORDER_COLORS.length];
    // const randomBgColor = getRandomItem(VIBRANT_BORDER_COLORS);
    return `<span class=${cx(css`
      background-color: ${randomBgColor}44;
      border: 1px solid ${randomBgColor}ee;
x    `)}>${matchedToken}</span>`;
  });

  return styledText;
};
const RenderTable = () => {
  const [inputText, setInputText] = useState("");
  const [anonymizedText, setAnonymizedText] = useState("");
  const [substitutedText, setSubstitutedText] = useState("");
  const [loadingData, setLoadingData] = useState(false);

  const handleClick = async () => {
    setLoadingData(true);
    const res = await chatApi.anonymizeText(inputText);
    const { textAnonymized, textSynthetic } = res.data ?? {};

    // setAnonymizedText(textAnonymized || "");
    setSubstitutedText(textSynthetic || "");

    const rezult = tokenizeAndStyleText(textAnonymized);
    setAnonymizedText(rezult);

    setLoadingData(false);
  };

  return (
    <>
      <div
        className={css`
          border: 1px solid ${colorPalette.strokePrimary};
        `}
      >
        <div
          className={css`
            display: flex;

            .header-border-right:not(:last-child) {
              border-right: 1px solid ${colorPalette.strokePrimary};
            }
          `}
        >
          <Header
            header="Wklej tekst tutaj"
            description="Surowy tekst do anonimizacji."
          />

          <Header
            header="Dane zanonimizowane"
            description="Tekst z danymi zastąpionymi tokenami"
          />

          <Header
            header="Dane zamienne"
            description="Tekst z przykładowymi wartościami pasującymi do tokenów."
          />
        </div>

        <div
          className={css`
            display: flex;

            .output-border-right:not(:last-child) {
              border-right: 1px solid ${colorPalette.strokePrimary};
            }
          `}
        >
          <div
            className={cx(
              "output-border-right",
              css`
                padding: 15px;
                width: 100%;
                height: 400px;
              `
            )}
          >
            <OutputTextArea value={inputText} onChange={setInputText} />
          </div>

          <div
            className={cx(
              "output-border-right",
              css`
                padding: 15px;
                width: 100%;
                height: 400px;
              `
            )}
          >
            {loadingData ? (
              <SkeletonTheme baseColor="#202020" highlightColor="#444">
                <div
                  id="ads"
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    height: "100%",
                    justifyContent: "space-between",
                  }}
                >
                  {Array.from({ length: 8 }).map((_, idx) => {
                    return (
                      <Skeleton
                        duration={idx * 0.1 + 1.8}
                        key={idx}
                        height={idx % 2 == 0 ? 20 : 40}
                        style={{
                          marginBottom: 16,
                        }}
                      />
                    );
                  })}
                </div>
              </SkeletonTheme>
            ) : (
              <div
                style={{
                  padding: "10px",
                }}
                dangerouslySetInnerHTML={{
                  __html: anonymizedText,
                }}
              >
                {/* {anonymizedText} */}
              </div>
              // <OutputTextArea
              //   value={anonymizedText}
              //   onChange={setInputText}
              //   readOnly
              // />
            )}
          </div>

          <div
            className={cx(
              "output-border-right",
              css`
                padding: 15px;
                width: 100%;
                height: 400px;
              `
            )}
          >
            {loadingData ? (
              <SkeletonTheme baseColor="#202020" highlightColor="#444">
                <div
                  id="ads"
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    height: "100%",
                    justifyContent: "space-between",
                  }}
                >
                  {Array.from({ length: 8 }).map((_, idx) => {
                    return (
                      <Skeleton
                        duration={idx * 0.1 + 1.8}
                        key={idx}
                        height={idx % 2 == 0 ? 20 : 40}
                        style={{
                          marginBottom: 16,
                        }}
                      />
                    );
                  })}
                </div>
              </SkeletonTheme>
            ) : (
              <OutputTextArea
                value={substitutedText}
                onChange={setInputText}
                readOnly
              />
            )}
          </div>
        </div>
      </div>
      <RunButton onClick={handleClick} />
    </>
  );
};

export default RenderTable;
