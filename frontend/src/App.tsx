import * as React from "react";
import * as ReactDOM from "react-dom";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import SearchPage from "./pages/SearchPage";
import RootPage from "./pages/RootPage";

import "./app.css"
import DocumentPage from "./pages/DocumentPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootPage />,
    children: [
      { index: true, element: <SearchPage /> },
      { path: "documents", element: <DocumentPage /> },
    ],
  },
]);

function App() {
  return (
    <div>
      <RouterProvider router={router} />
    </div>
  );
}

export default App;
