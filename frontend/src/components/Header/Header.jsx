import './header.css';

const Header = ({ text }) => {
    return ( 
        <p className='header'>
            {text}
        </p>
     );
}
 
export default Header;