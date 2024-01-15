import React from 'react';
import './search-button.css';

const SearchButton = ({ buttonText, isLoading }) => {
    return (
        <button type="submit" className="search-form__btn" disabled={isLoading}>
            {isLoading ? "Loading..." : buttonText}
        </button>
    );
};

export default SearchButton;
