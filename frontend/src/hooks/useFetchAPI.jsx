import { useState, useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";

import { settings } from "../utils";

export default function useFetchAPI(endpoint, options = {}) {
  const { getAccessTokenSilently } = useAuth0();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = await getAccessTokenSilently();
        setLoading(true);
        const response = await fetch(`${settings.api_base_url}${endpoint}`, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP Error! status: ${response.status}`);
        }

        const result = await response.json();
        setData(result);
      } catch (error) {
        setError(error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint, options]);

  return { data, loading, error };
}
