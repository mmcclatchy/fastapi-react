import React from "react";

import NavBarTabs from "./NavBarTabs";
import NavBarButtons from "./NavBarButtons";

export default function NavBar() {
  return (
    <div className="nav-bar">
      <NavBarTabs />
      <NavBarButtons />
    </div>
  );
}
