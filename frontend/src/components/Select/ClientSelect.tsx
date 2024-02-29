import React, { useState, useEffect } from "react";
import Select, { MultiValue } from "react-select";
import API from "../../Api";
import { useDocumentContext } from "../../context/DocumentContext";

interface ClientOption {
  value: string;
  label: string;
}

const ClientSelect = ({
  onClientChange,
}: {
  onClientChange: (params: string[]) => void;
}) => {
  const [clients, setClients] = useState<ClientOption[]>([]);
  const [selectedOptions, setSelectedOptions] = useState<ClientOption[]>([]);
  const [selectAllLabel, setSelectAllLabel] = useState<string>("Deselect all");
  const { documents, refetchDocuments } = useDocumentContext();

  useEffect(() => {
    onClientChange(selectedOptions.map((option) => option.value));
  }, [selectedOptions]);

  useEffect(() => {
    const clientNamesSet = new Set(documents.map((doc) => doc.clientName));
    const clientOptions = Array.from(clientNamesSet).map((name) => ({
      value: name,
      label: name,
    }));
    setClients(clientOptions);
    setSelectedOptions(clientOptions);
  }, [documents]);

  const handleChange = (selected: MultiValue<ClientOption>) => {
    if (selected.some((option) => option.value === "all")) {
      if (selectedOptions.length === clients.length) {
        setSelectedOptions([]);
        setSelectAllLabel("Select all");
      } else {
        setSelectedOptions(clients);
        setSelectAllLabel("Deselect all");
      }
    } else {
      setSelectedOptions([...selected]);
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
