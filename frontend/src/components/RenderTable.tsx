import { MdOutlineAutoAwesome } from "react-icons/md";
import { typography } from "../constants/typography";
import { css, cx } from "@emotion/css";
import colorPalette from "../constants/colorPalette";
import { useState } from "react";
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

const RenderTable = () => {
  const [inputText, setInputText] = useState("");
  const [anonymizedText, setAnonymizedText] = useState("");
  const [substitutedText, setSubstitutedText] = useState("");
  const [loadingData, setLoadingData] = useState(false);

  const handleClick = async () => {
    setLoadingData(true);
    const res = await chatApi.anonymizeText(inputText);
    const { textAnonymized, textSynthetic } = res.data ?? {};

    setAnonymizedText(textAnonymized || "");
    setSubstitutedText(textSynthetic || "");

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
              <OutputTextArea
                value={anonymizedText}
                onChange={setInputText}
                readOnly
              />
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
