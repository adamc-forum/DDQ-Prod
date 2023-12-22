import React from 'react';
import './search-button.css';

const SearchButton = ({ buttonText }) => {
    return (
        <button type="submit" className="search-form__btn">
            {buttonText}
        </button>
    );
};

export default SearchButton;
