import React, { useState } from 'react';
import SearchField from '../SearchField/SearchField';
import SearchButton from '../SearchButton/SearchButton';
import './search-form.css';

const SearchForm = ({ query, setQuery, handleSubmit, isLoading }) => {
    return (
        <form onSubmit={handleSubmit} className="search-form">
            <div className="search-form__input-section">
                <SearchField query={query} setQuery={setQuery} />
                <SearchButton buttonText="Search" isLoading={isLoading} />
            </div>
        </form>
    )
}

export default SearchForm