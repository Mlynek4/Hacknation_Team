import { MdOutlineAutoAwesome } from "react-icons/md";
import RenderTable from "./RenderTable";
import { css, cx } from "@emotion/css";
import { typography } from "../constants/typography";
const MainWrapper = () => {
  return (
    <div
      className={css`
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 25px;
        padding: 10px
      `}
    >
      <div
        className={cx(
          typography.textXl,
          css`
            display: flex;
            align-items: center;
            gap: 10px;
          `
        )}
      >
        <MdOutlineAutoAwesome />
        <span>Anonimizacja Dokumentów</span>
      </div>
      <RenderTable />
    </div>
  );
};

export default MainWrapper;
