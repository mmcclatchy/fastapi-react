import { useAuth0 } from "@auth0/auth0-react";
import React from "react";
import { NavBarTab } from "./NavBarTab";

export default function NavBarTabs() {
  const { isAuthenticated } = useAuth0();

  return (
    <div className="nav-bar__tabs">
      <NavBarTab path="/" label="Public" />
      {isAuthenticated && (
        <>
          <NavBarTab path="/me" label="My Info (protected)" />
        </>
      )}
    </div>
  );
}
