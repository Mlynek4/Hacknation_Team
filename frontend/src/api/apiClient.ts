import axios from "axios";

const backendApi = axios.create({
  // baseURL: "http://backend:8080",
  baseURL: "http://localhost:8080",
});


export default backendApi;
