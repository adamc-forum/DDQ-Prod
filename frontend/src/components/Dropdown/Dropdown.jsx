import React, { useState } from "react";
import "./dropdown.css";
import { Chevron } from "../Icons/Chevron";

// Renamed props for generality
const Dropdown = ({ selectedValue, setSelectedValue, optionsList }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleDropdown = (event) => {
    event.preventDefault();
    setIsOpen(!isOpen);
  }

  return (
    <div className="dropdown">
      <button className="dropdown-value" onClick={toggleDropdown}>
        <p>{selectedValue}</p>
        <span className={`dropdown-button ${isOpen && "open"}`}>
          <Chevron />
        </span>
      </button>
      {isOpen && (
        <div className={`dropdown-content ${isOpen && "open"}`}>
          {optionsList.map((option, index) => (
            <p
              key={index}
              className={`${
                selectedValue === option ? "selected" : "unselected"
              }`}
            >
              <button
                className="dropdown-content-button"
                onClick={() => {
                  setSelectedValue(option);
                  setIsOpen(false);
                }}
              >
                <span className="dropdown-content-button-text">{option}</span>
              </button>
            </p>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dropdown;
