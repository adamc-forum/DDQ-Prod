import React, { useState, useEffect } from "react";
import Select from "react-select";
import API from "../../Api";

const ClientSelect = ({ onClientChange }) => {
  const [clients, setClients] = useState([]);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [selectAllLabel, setSelectAllLabel] = useState("Deselect all");

  useEffect(() => {
    onClientChange(selectedOptions.map((option) => option.value));
  }, [selectedOptions]);

  useEffect(() => {
    API.get("/clients")
      .then((response) => {
        const clientOptions = response.data.clientNames.map((name) => ({
          value: name,
          label: name,
        }));
        setClients(clientOptions);
        setSelectedOptions(clientOptions); // Set all clients as selected by default
      })
      .catch((error) => console.error("Error fetching clients:", error));
  }, []);

  const handleChange = (selected) => {
    if (selected.some((option) => option.value === "all")) {
      if (selectedOptions.length === clients.length) {
        setSelectedOptions([]);
        setSelectAllLabel("Select all");
      } else {
        setSelectedOptions(clients);
        setSelectAllLabel("Deselect all");
      }
    } else {
      setSelectedOptions(selected);
      if (selected.length === clients.length) {
        setSelectAllLabel("Deselect all");
      } else {
        setSelectAllLabel("Select all");
      }
    }
  };

  const options = [{ value: "all", label: selectAllLabel }, ...clients];

  return (
    <Select
      isMulti
      options={options}
      value={selectedOptions}
      onChange={handleChange}
      placeholder="Select clients..."
    />
  );
};

export default ClientSelect;
