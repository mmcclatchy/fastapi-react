class Settings {
  constructor() {
    this.auth0_audience = process.env.REACT_APP_AUTH0_AUDIENCE;
    this.auth0_callback_url = process.env.REACT_APP_AUTH0_CALLBACK_URL;
    this.auth0_client_id = process.env.REACT_APP_AUTH0_CLIENT_ID;
    this.auth0_domain = process.env.REACT_APP_AUTH0_DOMAIN;
    this.api_base_url =
      process.env.REACT_APP_API_BASE_URL || "http://localhost:8080";
    this.env = process.env.NODE_ENV;
  }
}
const settings = new Settings();

const RequestMethods = {
  get: "GET",
  post: "POST",
  put: "PUT",
  patch: "PATCH",
  delete: "DELETE",
};

const RequestContentTypes = {
  json: "application/json",
  xWwwFormUrlencoded: "application/x-www-form-urlencoded",
  multipartFormData: "multipart/form-data",
  textPlain: "text/plain",
  xml: "application/xml",
  graphql: "application/graphql",
};

const RequestEnums = {
  methods: RequestMethods,
  contentTypes: RequestContentTypes,
};

export { settings, RequestEnums };
