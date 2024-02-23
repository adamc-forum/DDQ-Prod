import React from "react";
import SearchField from "../SearchField/SearchField";
import SearchButton from "../SearchButton/SearchButton";
import "./search-form.css";
import Dropdown from "../Dropdown/Dropdown";
import { RESULT_COUNT_LIST, SORT_OPTIONS_LIST, SortOption, ResultCount } from "../../constants";
import ClientSelect from "../Select/ClientSelect";

const SearchForm = ({
  query,
  setQuery,
  handleSubmit,
  isLoading,
  resultCount,
  setResultCount,
  sortOption,
  setSortOption,
  handleClientChange,
}: {
  query: string;
  setQuery: React.Dispatch<React.SetStateAction<string>>;
  handleSubmit: (e: React.KeyboardEvent | React.MouseEvent) => void;
  isLoading: boolean;
  resultCount: ResultCount;
  setResultCount: React.Dispatch<React.SetStateAction<ResultCount>>;
  sortOption: SortOption;
  setSortOption: React.Dispatch<React.SetStateAction<SortOption>>;
  handleClientChange: (params: string[]) => void;
}) => {
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleSubmit(event);
    }
  };

  return (
    <form className="search-form" onKeyDown={handleKeyDown}>
      <div className="search-form__input-section">
        <SearchField query={query} setQuery={setQuery} />
      </div>
      <div className="search-form__client-select">
        <span>Select Clients: </span>
        <ClientSelect onClientChange={handleClientChange} />
      </div>
      <div className="search-form__dropdown-group">
        <div>
          <span>Number of results: </span>
          <Dropdown<ResultCount>
            selectedValue={resultCount}
            setSelectedValue={setResultCount}
            optionsList={RESULT_COUNT_LIST}
          />
        </div>
        <div>
          <span>Sort results by: </span>
          <Dropdown
            selectedValue={sortOption}
            setSelectedValue={setSortOption}
            optionsList={SORT_OPTIONS_LIST}
          />
        </div>
      </div>
      <SearchButton
        buttonText="Search"
        isLoading={isLoading}
        handleSubmit={handleSubmit}
      />
    </form>
  );
};

export default SearchForm;
