import "./header.css";

const Header = ({ text }: { text: string }) => {
  return <p className="header">{text}</p>;
};

export default Header;
