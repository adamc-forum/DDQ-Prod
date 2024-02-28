import "./TableBtnGroup.css";

interface TableBtnGroupProps {
  selectedDocumentId: string | null;
  onAdd: () => void;
  onDelete: () => void;
}

const TableBtnGroup = ({
  selectedDocumentId,
  onAdd,
  onDelete,
}: TableBtnGroupProps) => {
  return (
    <div className="table__btngroup">
      <button onClick={onAdd} className="table__btngroup-add">
        Add
      </button>
      <button
        onClick={onDelete}
        className="table__btngroup-delete"
        disabled={!selectedDocumentId}
      >
        Delete
      </button>
    </div>
  );
};

export default TableBtnGroup;
