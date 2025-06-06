import "./Header.css";

function Header() {
  return (
    <header className="header-container">
      <h1 className="logo">
        <i className="fa-solid fa-comment"></i>
        RationTalk
      </h1>
      <p className="subtitle">
        Welcome to RationTalk, your interactive daily digest for news.
      </p>
    </header>
  );
}

export default Header;
