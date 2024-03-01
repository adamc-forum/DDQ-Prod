import { NavLink } from "react-router-dom";
import "./nav-links.css"

const NavLinks = () => {
  return (
    <nav className="nav-links">
      <NavLink
        to="/"
        className={({ isActive }) => (isActive ? "active" : "inactive")}
      >
        Search
      </NavLink>
      <NavLink
        to="/documents"
        className={({ isActive }) => (isActive ? "active" : "inactive")}
      >
        Documents
      </NavLink>
      <NavLink
        to="/upload"
        className={({ isActive }) => (isActive ? "active" : "inactive")}
      >
        Upload
      </NavLink>
    </nav>
  );
};

export default NavLinks;
