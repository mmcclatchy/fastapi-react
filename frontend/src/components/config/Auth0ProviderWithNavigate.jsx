import { Auth0Provider } from "@auth0/auth0-react";
import React from "react";
import { useNavigate } from "react-router-dom";

import { settings } from "../../utils";

export default function Auth0ProviderWithNavigate({ children }) {
  const navigate = useNavigate();

  const onRedirectCallback = (appState) => {
    navigate(appState?.returnTo || window.location.pathname);
  };
  const { auth0_audience, auth0_callback_url, auth0_client_id, auth0_domain } =
    settings;

  if (
    !(auth0_domain && auth0_client_id && auth0_callback_url && auth0_audience)
  ) {
    const missing = [];
    !auth0_domain && missing.push("auth0_domain");
    !auth0_client_id && missing.push("auth0_client_id");
    !auth0_callback_url && missing.push("auth0_callback_url");
    !auth0_audience && missing.push("auth0_audience");
    return <p>Missing: {missing.join(", ")}</p>;
  }

  return (
    <Auth0Provider
      domain={auth0_domain}
      clientId={auth0_client_id}
      authorizationParams={{
        audience: auth0_audience,
        redirect_uri: auth0_callback_url,
      }}
      onRedirectCallback={onRedirectCallback}
    >
      {children}
    </Auth0Provider>
  );
}
