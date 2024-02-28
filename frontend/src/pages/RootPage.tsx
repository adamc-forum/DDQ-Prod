import { Outlet } from "react-router-dom";
import NavLinks from "../components/NavBar/NavLinks";
import Header from "../components/Header/Header";
import "./root-page.css";

const RootPage = () => {
  return (
    <div className="root-page">
      <div className="navbar">
        <Header text={"REIIF DDQ Assistant"} />
        <NavLinks />
      </div>
      <Outlet />
    </div>
  );
};

export default RootPage;
