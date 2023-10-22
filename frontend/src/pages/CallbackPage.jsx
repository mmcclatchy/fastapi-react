import { useAuth0 } from "@auth0/auth0-react";
import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function CallbackPage() {
  const { error } = useAuth0();
  const navigate = useNavigate();

  useEffect(() => {
    if (error) return <div className="error">{JSON.stringify(error)}</div>;
    navigate("/me");
  }, [error, navigate]);

  return <p>Loading...</p>;
}
