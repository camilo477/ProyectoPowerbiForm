import axios from "axios";

export const login = async (credentials) => {
  const res = await axios.post("/api/token/", credentials);
  return res.data;
};

export const register = (email, username, password, accessToken) => {
    return axios.post(
        "http://localhost:8000/api/accounts/register/",
        { email, username, password },
        {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        }
    );
};

export const setAuthToken = (token) => {
  if (token) {
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("authToken", token);
  } else {
    delete axios.defaults.headers.common["Authorization"];
    localStorage.removeItem("authToken");
  }
};
