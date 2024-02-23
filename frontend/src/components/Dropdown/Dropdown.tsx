import React, { useState } from "react";
import "./dropdown.css";
import { Chevron } from "../Icons/Chevron";

// Renamed props for generality
function Dropdown<T>({
  selectedValue,
  setSelectedValue,
  optionsList,
}: {
  selectedValue: T;
  setSelectedValue: React.Dispatch<React.SetStateAction<T>>;
  optionsList: readonly T[];
}) {
  const [isOpen, setIsOpen] = useState(false);

  const toggleDropdown = (event: React.MouseEvent | React.KeyboardEvent) => {
    event.preventDefault();
    setIsOpen(!isOpen);
  };

  return (
    <div className="dropdown">
      <button className="dropdown-value" onClick={toggleDropdown}>
        <p>{String(selectedValue)}</p>
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
                <span className="dropdown-content-button-text">{String(option)}</span>
              </button>
            </p>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dropdown;
