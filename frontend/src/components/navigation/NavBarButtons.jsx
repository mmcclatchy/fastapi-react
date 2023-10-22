import { useAuth0 } from "@auth0/auth0-react";
import React from "react";

import LogoutButton from "../buttons/LogoutButton";
import SignupButton from "../buttons/SignupButton";
import LoginButton from "../buttons/LoginButton";

export default function NavBarButtons() {
  const { isAuthenticated } = useAuth0();

  return (
    <div className="nav-bar__buttons">
      {isAuthenticated ? (
        <LogoutButton />
      ) : (
        <>
          <SignupButton />
          <LoginButton />
        </>
      )}
    </div>
  );
}
