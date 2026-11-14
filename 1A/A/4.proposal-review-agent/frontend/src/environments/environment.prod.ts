// Production build: same origin. nginx (compose) or the frontend Cloud Run service proxies /api.
// The dev UI link only shows when the backend reports ENABLE_ADK_WEB=true (local compose).
export const environment = {
  apiUrl: '',
  adkWebUrl: 'http://localhost:8000/dev-ui/',
};
