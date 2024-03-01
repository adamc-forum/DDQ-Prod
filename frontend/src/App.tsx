import React, { useEffect, useState } from "react";
import * as ReactDOM from "react-dom";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { DocumentProvider } from "./context/DocumentContext"; // Import DocumentProvider

import SearchPage from "./pages/SearchPage";
import RootPage from "./pages/RootPage";
import DocumentPage from "./pages/DocumentPage";
import UploadPage from "./pages/UploadPage";

import "./app.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootPage />,
    children: [
      { index: true, element: <SearchPage /> },
      { path: "documents", element: <DocumentPage /> },
      { path: "upload", element: <UploadPage /> },
    ],
  },
]);

function App() {
  return (
    <div>
      <DocumentProvider>
        <RouterProvider router={router} />
      </DocumentProvider>
    </div>
  );
}

export default App;
