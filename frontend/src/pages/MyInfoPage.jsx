import React, { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

// import useFetchAPI from "../hooks/useFetchAPI"
import { RequestEnums, settings } from "../utils";

const DataList = ({ data }) => {
  return (
    <ul>
      {Object.entries(data).map(([key, val]) => (
        <li key={key}>
          {key}: {val}
        </li>
      ))}
    </ul>
  );
};

const TokenInfo = () => {
  const { user } = useAuth0();

  if (!user) return <p>Loading...</p>;

  return (
    <div className="token-info">
      <h2>Token Info:</h2>
      <DataList data={user} />
    </div>
  );
};

const DatabaseInfo = () => {
  const { getAccessTokenSilently } = useAuth0();
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = await getAccessTokenSilently();
        const response = await fetch(`${settings.api_base_url}/v1/users/me`, {
          method: RequestEnums.methods.get,
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP Error! status: ${response.status}`);
        }

        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [getAccessTokenSilently]);

  if (!data) return <p>Loading...</p>;

  return (
    <div className="database-info">
      <h2>Database Info:</h2>
      <DataList data={data} />
    </div>
  );
};

export default function MyInfoPage() {
  return (
    <div className="my-info">
      <TokenInfo />
      <DatabaseInfo />
    </div>
  );
}
