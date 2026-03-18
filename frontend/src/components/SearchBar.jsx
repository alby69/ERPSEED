import { useState } from 'react';

function SearchBar({ onSearch, placeholder = "Cerca..." }) {
  const [term, setTerm] = useState('');

  const handleSearch = () => {
    onSearch(term);
  };

  return (
    <div className="d-flex gap-2">
      <input 
        type="text" 
        className="form-control" 
        placeholder={placeholder}
        value={term}
        onChange={(e) => setTerm(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
      />
      <button className="btn btn-outline-secondary" onClick={handleSearch}>Cerca</button>
    </div>
  );
}

export default SearchBar;