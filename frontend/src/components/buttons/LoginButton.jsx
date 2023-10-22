import { useAuth0 } from "@auth0/auth0-react";
import React from "react";

export default function LoginButton() {
  const { loginWithRedirect } = useAuth0();

  const handleLogin = async () => {
    await loginWithRedirect({
      appState: {
        returnTo: "/callback",
      },
      authorizationParams: {
        prompt: "login",
      },
    });
  };

  return (
    <button className="button__login" onClick={handleLogin}>
      Log In
    </button>
  );
}
