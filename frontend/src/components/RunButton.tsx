import { css, cx } from "@emotion/css";
import colorPalette from "../constants/colorPalette";
import { typography } from "../constants/typography";
import { FaLock } from "react-icons/fa6";
const RunButton = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className={cx(
        typography.textM,
        css`
          border-radius: 8px;
          border: 1px solid ${colorPalette.strokePrimary};
          width: fit-content;
          padding: 10px 15px;
          color: ${colorPalette.primary};
          cursor: pointer;
          transition: all 0.2s ease-in-out;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 8px;

          &:hover {
            border-color: ${colorPalette.primary};
            background-color: ${colorPalette.primary};
            color: ${colorPalette.background};
          }
        `
      )}
    >
      Anonimizuj
      <FaLock />
    </button>
  );
};

export default RunButton;
