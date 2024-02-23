import React from "react";
import "./search-button.css";

const SearchButton = ({
  buttonText,
  isLoading,
  handleSubmit,
}: {
  buttonText: string;
  isLoading: boolean;
  handleSubmit: (e: React.KeyboardEvent | React.MouseEvent) => void;
}) => {
  const onClick = (event: React.KeyboardEvent | React.MouseEvent) => {
    console.log("clicked");
    event.preventDefault();
    handleSubmit(event);
  };

  return (
    <button
      type="submit"
      onClick={onClick}
      className="search-form__btn"
      disabled={isLoading}
    >
      {isLoading ? "Loading..." : buttonText}
    </button>
  );
};

export default SearchButton;
