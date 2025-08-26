import React, { useEffect, useState } from 'react';
import './collapsible.css';

const Collapsible = ( {
  id,
  label,
  children,
  disabled=false,
  startOpen=false,
  autoOpenWhenEnabled=false,
} ) => {
  const storageKey = `collapsible:${id}`;

  const [open, setOpen] = useState(() => {
    const saved = sessionStorage.getItem(storageKey);
    if (saved != null) return saved === "1";
    return startOpen;
  });

  // Persist state
  useEffect(() => {
    sessionStorage.setItem(storageKey, open ? "1" : "0");
  }, [storageKey, open]);

  // Auto-open when innings starts
  useEffect(() => {
    if (autoOpenWhenEnabled && !disabled && !open) {
      setOpen(true);
    }
  }, [autoOpenWhenEnabled, disabled, open]);

  const toggle = () => {
    if (!disabled) setOpen((o) => !o);
  };

  return (
    <div>
      <button 
        className={open ? "collapse-open" : "collapse-shut"}
        onClick={toggle}
        disabled={disabled}
      >
        {label}
      </button>

      {open && (
        <div className={"content-show"}>
          <div className='content'>{children}</div>
        </div>
      )}
    </div>
  );
};

export default Collapsible;