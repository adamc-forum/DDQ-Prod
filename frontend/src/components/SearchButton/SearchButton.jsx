import React from 'react';
import './search-button.css';

const SearchButton = ({ buttonText, isLoading, handleSubmit }) => {

    const onClick = (event) => {
        console.log("clicked");
        event.preventDefault();
        handleSubmit()
    }

    return (
        <button type="submit" onClick={onClick} className="search-form__btn" disabled={isLoading}>
            {isLoading ? "Loading..." : buttonText}
        </button>
    );
};

export default SearchButton;
